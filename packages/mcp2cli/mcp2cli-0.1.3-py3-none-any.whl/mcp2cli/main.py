import asyncio
import inspect
import json
import os
import typer
import click
from enum import Enum
from rich.console import Console
from rich.table import Table
from typing import Optional, List, Dict, Any, Tuple, Union

from mcp.types import Tool, LoggingMessageNotification, SamplingMessage
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.stdio import stdio_client, StdioServerParameters


console = Console()


class MCPCLI:
    """
    A CLI for MCP servers, dynamically generating commands from tool definitions.
    """

    def __init__(self, config_path: str = "mcp.json"):
        """
        Initializes the MCPCLI, loading server configurations and setting up the Typer app.
        """
        self.config_path = config_path
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.tools: Dict[str, List[str]] = {}  # server_name -> list of tool_names
        self.tool_to_servers: Dict[str, List[str]] = {}  # tool_name -> list of server_names
        self._app = typer.Typer(rich_markup_mode="rich", add_help_option=True, pretty_exceptions_show_locals=False)
        self._app.callback(invoke_without_command=True)(self.main)

    def _show_help(self):
        """
        Displays all available tools from all servers in a table, grouped by server.
        """
        table = Table(title="[bold]Available MCP Tools[/bold]")
        table.add_column("Server", style="cyan", no_wrap=True)
        table.add_column("Tool Name", style="magenta")
        table.add_column("Description", style="green")

        for server_name, tools in sorted(self.tools.items()):
            if tools:
                server_config = self.servers.get(server_name, {})
                for i, tool_name in enumerate(sorted(tools)):
                    tool_def = next((t for t in server_config.get("tools", []) if t.name == tool_name), None)
                    description = tool_def.description if tool_def else ""
                    if i == 0:
                        table.add_row(f"[bold]{server_name}[/bold]", tool_name, description, end_section=True if len(tools) == 1 else False)
                    else:
                        table.add_row("", tool_name, description, end_section=True if i == len(tools) - 1 else False)
        
        console.print(table)

    def main(self, ctx: typer.Context):
        """
        A CLI for MCP servers.
        """
        if ctx.invoked_subcommand is None:
            self._show_help()

    async def _get_client_session(self, server_name: str):
        server_config = self.servers[server_name]
        
        if "url" in server_config:
            return streamablehttp_client(server_config["url"])
        elif "command" in server_config:
            command_parts = server_config["command"].split()
            command = command_parts[0]
            args = command_parts[1:] + server_config.get("args", [])
            env = server_config.get("env", {})
            params = StdioServerParameters(command=command, args=args, env=env)
            return stdio_client(params)
        else:
            raise ValueError(f"Unknown or invalid transport configuration for server {server_name}")

    async def _load_server_tools(self, server_name: str, server_config: Dict[str, Any]):
        """Load tools from server using improved session management to avoid TaskGroup issues."""
        session = None
        transport_context = None
        
        try:
            transport_context = await self._get_client_session(server_name)
            tools = []
            
            if 'command' in server_config:
                # Handle stdio connection
                try:
                    client_streams = await transport_context.__aenter__()
                    read, write = client_streams
                    
                    session = ClientSession(read, write)
                    await session.__aenter__()
                    await session.initialize()
                    tool_list = await session.list_tools()
                    tools = tool_list.tools
                except Exception as e:
                    raise Exception(f"Failed to connect via stdio: {e}") from e
            else:
                # Handle HTTP/SSE connection
                try:
                    transport_streams = await transport_context.__aenter__()
                    read, write, _ = transport_streams
                    
                    session = ClientSession(read, write)
                    await session.__aenter__()
                    await session.initialize()
                    tool_list = await session.list_tools()
                    tools = tool_list.tools
                except Exception as e:
                    raise Exception(f"Failed to connect via HTTP: {e}") from e

            self.servers[server_name]["tools"] = tools
            tool_names = [tool.name for tool in tools]
            self.tools[server_name] = tool_names
            
            for tool in tools:
                if tool.name not in self.tool_to_servers:
                    self.tool_to_servers[tool.name] = []
                self.tool_to_servers[tool.name].append(server_name)
                
        except Exception as e:
            console.print(f"Error connecting to server '{server_name}': {e}", style="bold red")
            import traceback
            traceback.print_exc()
        finally:
            # Clean up in reverse order
            if session:
                try:
                    await session.__aexit__(None, None, None)
                except Exception as e:
                    console.print(f"Session cleanup warning for {server_name}: {e}", style="yellow")
            
            if transport_context:
                try:
                    await transport_context.__aexit__(None, None, None)
                except Exception as e:
                    console.print(f"Transport cleanup warning for {server_name}: {e}", style="yellow")

    def _add_tool_commands(self):
        for tool_name, server_names in self.tool_to_servers.items():
            first_server_name = server_names[0]
            server_config = self.servers[first_server_name]
            tool_def = next((t for t in server_config.get("tools", []) if t.name == tool_name), None)
            
            if tool_def:
                command_callback = self._create_command_callback(tool_name, tool_def, len(server_names) > 1)
                self._app.command(name=tool_name, help=tool_def.description)(command_callback)

    async def _load_all_servers(self):
        if not os.path.exists(self.config_path):
            console.print(f"Error: Configuration file not found at {self.config_path}", style="bold red")
            raise typer.Exit(code=1)
            
        with open(self.config_path, "r") as f:
            config = json.load(f)

        self.servers = config.get("servers", config.get("mcpServers", {}))
        for name, conf in self.servers.items():
            try:
                await self._load_server_tools(name, conf)
            except Exception as e:
                console.print(f"Failed to load server '{name}': {e}", style="bold red")

    def _parse_schema_type(self, param_name: str, schema: Dict[str, Any]) -> Tuple[type, typer.Option]:
        """Parse JSON Schema type and return Python type and typer.Option"""
        schema_type = schema.get("type", "string")
        description = schema.get("description", "")
        default_value = schema.get("default", None)
        
        # Handle $ref types (Pydantic models) first - they override the type field
        if "$ref" in schema and hasattr(self, '_current_tool_schema'):
            ref_path = schema["$ref"]
            if ref_path.startswith("#/$defs/") and "$defs" in self._current_tool_schema:
                model_name = ref_path.split("/")[-1]
                model_def = self._current_tool_schema["$defs"].get(model_name, {})
                if "properties" in model_def:
                    structure_hint = self._build_structure_hint(model_def["properties"])
                    
                    help_text = f"{description} (JSON string){structure_hint}" if description else f"JSON string{structure_hint}"
                    
                    typer_option = typer.Option(
                        default_value,
                        f"--{param_name}",
                        help=help_text
                    )
                    return str, typer_option
        
        # Handle enum types
        elif "enum" in schema:
            enum_values = schema["enum"]
            param_type = str
            choices_text = '|'.join(map(str, enum_values))
            help_text = f"{description} [{choices_text}]" if description else f"[{choices_text}]"
            
            typer_option = typer.Option(
                default_value, 
                f"--{param_name}",
                help=help_text
            )
            return param_type, typer_option
        
        # Handle array types
        elif schema_type == "array":
            param_type = List[str]  # Default to string items
            items_schema = schema.get("items", {})
            items_type = items_schema.get("type", "string")
            
            if items_type == "integer":
                param_type = List[int]
            elif items_type == "number":
                param_type = List[float]
            elif items_type == "boolean":
                param_type = List[bool]
            
            typer_option = typer.Option(
                default_value or [],
                f"--{param_name}",
                help=f"{description} (can be specified multiple times)"
            )
            return param_type, typer_option
        
        # Handle object types
        elif schema_type == "object":
            param_type = str  # JSON string input
            
            # Handle direct properties in the schema
            structure_hint = ""
            if "properties" in schema:
                structure_hint = self._build_structure_hint(schema["properties"])
            
            help_text = f"{description} (JSON string){structure_hint}" if description else f"JSON string{structure_hint}"
            
            typer_option = typer.Option(
                default_value,
                f"--{param_name}",
                help=help_text
            )
            return param_type, typer_option
        
        # Handle basic types
        elif schema_type == "integer":
            param_type = int
            help_text = self._add_numeric_constraints_to_help(description, schema)
        elif schema_type == "number":
            param_type = float
            help_text = self._add_numeric_constraints_to_help(description, schema)
        elif schema_type == "boolean":
            param_type = bool
            help_text = description
        else:
            param_type = str
            help_text = self._add_string_constraints_to_help(description, schema)
        
        typer_option = typer.Option(
            default_value,
            f"--{param_name}",
            help=help_text
        )
        return param_type, typer_option

    def _add_numeric_constraints_to_help(self, description: str, schema: Dict[str, Any]) -> str:
        """Add numeric constraints to help text"""
        constraints = []
        
        if "minimum" in schema:
            constraints.append(f">= {schema['minimum']}")
        elif "exclusiveMinimum" in schema:
            constraints.append(f"> {schema['exclusiveMinimum']}")
            
        if "maximum" in schema:
            constraints.append(f"<= {schema['maximum']}")
        elif "exclusiveMaximum" in schema:
            constraints.append(f"< {schema['exclusiveMaximum']}")
        
        if constraints:
            constraint_text = ", ".join(constraints)
            return f"{description} [{constraint_text}]" if description else f"[{constraint_text}]"
        
        return description

    def _add_string_constraints_to_help(self, description: str, schema: Dict[str, Any]) -> str:
        """Add string constraints to help text"""
        constraints = []
        
        if "minLength" in schema:
            constraints.append(f"min length: {schema['minLength']}")
        if "maxLength" in schema:
            constraints.append(f"max length: {schema['maxLength']}")
        if "pattern" in schema:
            constraints.append(f"pattern: {schema['pattern']}")
        
        if constraints:
            constraint_text = ", ".join(constraints)
            return f"{description} [{constraint_text}]" if description else f"[{constraint_text}]"
        
        return description

    def _build_structure_hint(self, properties: Dict[str, Any]) -> str:
        """Build a structure hint from JSON Schema properties"""
        # Don't show misleading generic examples
        return ""

    def _process_arguments(self, tool_def: Tool, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate arguments based on schema types"""
        processed = {}
        schema_properties = tool_def.inputSchema.get("properties", {})
        required_params = tool_def.inputSchema.get("required", [])
        
        # Check for missing required parameters
        for required_param in required_params:
            if required_param not in kwargs or kwargs[required_param] is None:
                raise typer.BadParameter(f"Missing required parameter: --{required_param}")
        
        for param_name, value in kwargs.items():
            if param_name == 'server_name' or value is None:
                continue
                
            param_schema = schema_properties.get(param_name, {})
            schema_type = param_schema.get("type", "string")
            
            try:
                # Handle object types - parse JSON string
                if schema_type == "object" and isinstance(value, str):
                    processed[param_name] = json.loads(value)
                    self._validate_object_schema(processed[param_name], param_schema, param_name)
                
                # Handle array types - validate items
                elif schema_type == "array" and isinstance(value, list):
                    processed[param_name] = self._validate_array_items(value, param_schema, param_name)
                
                # Handle enum validation
                elif "enum" in param_schema:
                    if value not in param_schema["enum"]:
                        enum_values = ", ".join(map(str, param_schema["enum"]))
                        raise typer.BadParameter(f"Invalid value '{value}' for {param_name}. Must be one of: {enum_values}")
                    processed[param_name] = value
                
                # Handle numeric validation
                elif schema_type in ["integer", "number"]:
                    processed[param_name] = value
                    self._validate_numeric_constraints(value, param_schema, param_name)
                
                # Handle string validation
                elif schema_type == "string":
                    processed[param_name] = value
                    self._validate_string_constraints(value, param_schema, param_name)
                
                else:
                    processed[param_name] = value
                    
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                raise typer.BadParameter(f"Invalid value for parameter {param_name}: {e}")
                
        return processed
    
    def _validate_object_schema(self, obj: Any, schema: Dict[str, Any], param_name: str):
        """Validate object against its schema"""
        if not isinstance(obj, dict):
            raise ValueError(f"Expected object (dictionary) for {param_name}")
            
        # Basic validation - could be enhanced with full JSON Schema validation
        if "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                if prop_name in obj:
                    prop_type = prop_schema.get("type", "string")
                    prop_value = obj[prop_name]
                    
                    if prop_type == "integer" and not isinstance(prop_value, int):
                        raise ValueError(f"Property {prop_name} must be an integer")
                    elif prop_type == "number" and not isinstance(prop_value, (int, float)):
                        raise ValueError(f"Property {prop_name} must be a number")
                    elif prop_type == "boolean" and not isinstance(prop_value, bool):
                        raise ValueError(f"Property {prop_name} must be a boolean")
                    elif prop_type == "string" and not isinstance(prop_value, str):
                        raise ValueError(f"Property {prop_name} must be a string")
    
    def _validate_array_items(self, arr: List[Any], schema: Dict[str, Any], param_name: str) -> List[Any]:
        """Validate array items against schema"""
        items_schema = schema.get("items", {})
        items_type = items_schema.get("type", "string")
        
        validated = []
        for i, item in enumerate(arr):
            if items_type == "integer":
                if not isinstance(item, int):
                    try:
                        validated.append(int(item))
                    except (ValueError, TypeError):
                        raise ValueError(f"Array item {i} must be an integer")
                else:
                    validated.append(item)
            elif items_type == "number":
                if not isinstance(item, (int, float)):
                    try:
                        validated.append(float(item))
                    except (ValueError, TypeError):
                        raise ValueError(f"Array item {i} must be a number")
                else:
                    validated.append(item)
            elif items_type == "boolean":
                if not isinstance(item, bool):
                    if isinstance(item, str):
                        if item.lower() in ('true', '1', 'yes'):
                            validated.append(True)
                        elif item.lower() in ('false', '0', 'no'):
                            validated.append(False)
                        else:
                            raise ValueError(f"Array item {i} must be a boolean")
                    else:
                        raise ValueError(f"Array item {i} must be a boolean")
                else:
                    validated.append(item)
            else:
                validated.append(str(item))
                
        return validated
    
    def _validate_numeric_constraints(self, value: Union[int, float], schema: Dict[str, Any], param_name: str):
        """Validate numeric constraints like minimum, maximum"""
        if "minimum" in schema and value < schema["minimum"]:
            raise ValueError(f"{param_name} must be >= {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            raise ValueError(f"{param_name} must be <= {schema['maximum']}")
        if "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
            raise ValueError(f"{param_name} must be > {schema['exclusiveMinimum']}")
        if "exclusiveMaximum" in schema and value >= schema["exclusiveMaximum"]:
            raise ValueError(f"{param_name} must be < {schema['exclusiveMaximum']}")
    
    def _validate_string_constraints(self, value: str, schema: Dict[str, Any], param_name: str):
        """Validate string constraints like minLength, maxLength, pattern"""
        if "minLength" in schema and len(value) < schema["minLength"]:
            raise ValueError(f"{param_name} must be at least {schema['minLength']} characters long")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            raise ValueError(f"{param_name} must be at most {schema['maxLength']} characters long")
        if "pattern" in schema:
            import re
            if not re.match(schema["pattern"], value):
                raise ValueError(f"{param_name} does not match required pattern: {schema['pattern']}")

    def _create_command_callback(self, tool_name: str, tool_def: Tool, needs_server_option: bool):
        
        def callback(
            ctx: typer.Context,
            server_name: Optional[str] = typer.Option(None, "--server-name", help="Specify the server for the command."),
            **kwargs
        ):
            async def async_main():
                chosen_server = server_name
                if not chosen_server:
                    server_options = self.tool_to_servers.get(tool_name, [])
                    if len(server_options) == 1:
                        chosen_server = server_options[0]
                    else:
                        console.print(f"Tool '{tool_name}' is available on multiple servers: {server_options}. Please specify one with --server-name.", style="bold red")
                        raise typer.Exit(code=1)

                params = self._process_arguments(tool_def, kwargs)
                
                try:
                    server_config = self.servers[chosen_server]
                    transport_context = await self._get_client_session(chosen_server)
                    session = None

                    async def process_result(session):
                        await session.initialize()
                        call_result = await session.call_tool(tool_name, params)

                        # If the result is async iterable (streaming)
                        if hasattr(call_result, "__aiter__"):
                            final_result = None
                            async for item in call_result:
                                if isinstance(item, LoggingMessageNotification):
                                    if item.params and hasattr(item.params, 'data') and isinstance(item.params.data, str):
                                        console.print(item.params.data, end="")
                                elif isinstance(item, SamplingMessage) and item.role == "assistant":
                                    if hasattr(item.content, 'text'):
                                        final_result = item.content.text

                            if final_result is not None:
                                # Try to coerce to int/float if possible
                                try:
                                    result_val = int(final_result)
                                except (ValueError, TypeError):
                                    try:
                                        result_val = float(final_result)
                                    except (ValueError, TypeError):
                                        result_val = final_result
                                console.print(json.dumps({"result": result_val}))
                        else:
                            # Non-streaming result (e.g., CallToolResult)
                            result_val = None
                            # Prefer structuredContent if available
                            if hasattr(call_result, "structuredContent") and call_result.structuredContent is not None:
                                sc = call_result.structuredContent
                                if isinstance(sc, dict) and "result" in sc:
                                    result_val = sc["result"]
                                else:
                                    result_val = sc
                            elif hasattr(call_result, "content") and call_result.content:
                                # content may be list of TextContent objects
                                first = call_result.content[0] if isinstance(call_result.content, list) else call_result.content
                                if hasattr(first, "text"):
                                    try:
                                        result_val = int(first.text)
                                    except (ValueError, TypeError):
                                        try:
                                            result_val = float(first.text)
                                        except (ValueError, TypeError):
                                            result_val = first.text
                            else:
                                # Fallback: the object itself might be JSON serialisable
                                result_val = call_result

                            console.print(json.dumps({"result": result_val}))

                    try:
                        if 'command' in server_config:
                            # Handle stdio connection
                            client_streams = await transport_context.__aenter__()
                            read, write = client_streams
                            
                            session = ClientSession(read, write)
                            await session.__aenter__()
                            await process_result(session)
                        else:
                            # Handle HTTP/SSE connection
                            transport_streams = await transport_context.__aenter__()
                            read, write, _ = transport_streams
                            
                            session = ClientSession(read, write)
                            await session.__aenter__()
                            await process_result(session)
                    finally:
                        # Clean up in reverse order
                        if session:
                            try:
                                await session.__aexit__(None, None, None)
                            except Exception as e:
                                console.print(f"Session cleanup warning: {e}", style="yellow")
                        
                        if transport_context:
                            try:
                                await transport_context.__aexit__(None, None, None)
                            except Exception as e:
                                console.print(f"Transport cleanup warning: {e}", style="yellow")

                except Exception as e:
                    console.print(f"Error calling tool {tool_name} on server {chosen_server}: {e}", style="bold red")

            asyncio.run(async_main())

        # Dynamically create the signature for Typer
        sig_params = [
             inspect.Parameter('ctx', inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ]

        if needs_server_option:
             sig_params.append(inspect.Parameter('server_name', inspect.Parameter.KEYWORD_ONLY, annotation=Optional[str], default=typer.Option(None, "--server-name", help="Specify the server for the command.")))
        else:
             sig_params.append(inspect.Parameter('server_name', inspect.Parameter.KEYWORD_ONLY, annotation=Optional[str], default=typer.Option(None, "--server-name", help="Specify the server for the command.", hidden=True)))


        # Store the full schema for reference during parameter parsing
        self._current_tool_schema = tool_def.inputSchema
        
        for p_name, p_schema in tool_def.inputSchema.get("properties", {}).items():
            param_type, typer_option = self._parse_schema_type(p_name, p_schema)
            
            sig_params.append(
                inspect.Parameter(
                    p_name,
                    inspect.Parameter.KEYWORD_ONLY,
                    annotation=param_type,
                    default=typer_option
                )
            )

        callback.__signature__ = inspect.Signature(parameters=sig_params)
        return callback

    async def _prepare_cli(self):
        await self._load_all_servers()
        self._add_tool_commands()

    def run(self):
        """
        Loads all servers and runs the Typer application.
        """
        self._app()


def run_cli():
    """Initializes and runs the MCP-CLI application."""
    import sys
    
    # Simple config parsing from command line
    config_path = "mcp.json"
    if "--config" in sys.argv:
        config_index = sys.argv.index("--config")
        if config_index + 1 < len(sys.argv):
            # Only treat as config if it's before any command
            is_global_config = True
            for i, arg in enumerate(sys.argv[1:], 1):
                if i >= config_index:
                    break
                if not arg.startswith('-'):
                    is_global_config = False
                    break
            
            if is_global_config:
                config_path = sys.argv[config_index + 1]
                # Remove config args so they don't interfere with tool commands
                sys.argv.pop(config_index)  # Remove --config
                sys.argv.pop(config_index)  # Remove the path
    
    cli = MCPCLI(config_path)
    try:
        asyncio.run(cli._prepare_cli())
        cli.run()
    except Exception as e:
        console.print(f"Failed to prepare CLI: {e}", style="bold red")

if __name__ == "__main__":
    run_cli()
