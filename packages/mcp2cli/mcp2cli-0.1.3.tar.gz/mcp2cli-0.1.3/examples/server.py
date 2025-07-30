import typer
from fastmcp import FastMCP
from typing import List, Dict, Any, Annotated, Literal
from pydantic import BaseModel, Field
import json

mcp = FastMCP(name="Enhanced Type Example Server")
app = typer.Typer()

# Enum example using Literal
@mcp.tool
def enum_example(
    mode: Annotated[
        Literal["debug", "production", "test"], 
        Field(description="Operation mode")
    ]
) -> str:
    """Example tool with enum parameter using Literal type."""
    return f"Running in {mode} mode"

# Array example with validation
@mcp.tool
def array_example(
    numbers: Annotated[
        List[int], 
        Field(description="List of integers to sum", min_length=1)
    ]
) -> int:
    """Example tool with array parameter."""
    return sum(numbers)

# Object example using Pydantic model
class ConfigModel(BaseModel):
    name: str = Field(description="Configuration name")
    port: int = Field(description="Port number", ge=1, le=65535)
    enabled: bool = Field(description="Whether the config is enabled")

@mcp.tool
def object_example(
    config: Annotated[ConfigModel, Field(description="Configuration object")]
) -> str:
    """Example tool with object parameter using Pydantic model."""
    return f"Config received: {json.dumps(config.model_dump(), indent=2)}"

# Numeric constraints example
@mcp.tool
def numeric_constraints(
    value: Annotated[int, Field(description="Integer between 1 and 100", ge=1, le=100)],
    percentage: Annotated[float, Field(description="Float between 0.0 and 1.0", ge=0.0, le=1.0)]
) -> str:
    """Example tool with numeric constraints."""
    return f"Value: {value}, Percentage: {percentage * 100}%"

# String constraints example
@mcp.tool
def string_constraints(
    text: Annotated[str, Field(description="Text between 3 and 50 characters", min_length=3, max_length=50)]
) -> str:
    """Example tool with string constraints."""
    return f"Text length: {len(text)}, Content: {text}"

# Mixed types example
class SettingsModel(BaseModel):
    timeout: int = Field(description="Timeout in seconds", ge=1)
    retry: bool = Field(description="Whether to retry on failure")

@mcp.tool
def mixed_types(
    mode: Annotated[Literal["fast", "slow", "medium"], Field(description="Operation mode")],
    tags: Annotated[List[str], Field(description="List of string tags", min_length=1)],
    settings: Annotated[SettingsModel, Field(description="Configuration settings")],
    count: Annotated[int, Field(description="Number of operations", ge=1, le=10)] = 1
) -> str:
    """Example tool with mixed parameter types."""
    return f"Mode: {mode}, Tags: {tags}, Settings: {settings.model_dump()}, Count: {count}"

@app.command()
def main(
    transport: str = typer.Option("stdio", "--transport", "-t", help="The transport to use (stdio or http)."),
    port: int = typer.Option(8000, "--port", "-p", help="The port to use for HTTP transport.")
):
    """
    Run the enhanced type example MCP server.
    """
    if transport == "http":
        mcp.run(transport="sse", port=port, show_banner=False)
    else:
        mcp.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    app()