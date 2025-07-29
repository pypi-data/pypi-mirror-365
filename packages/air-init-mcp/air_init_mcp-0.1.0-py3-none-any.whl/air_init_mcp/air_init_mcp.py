"""Main module."""

from fastmcp import FastMCP

mcp = FastMCP("Air Init MCP Server")


@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"


@mcp.tool
def air_init(domain_name: str) -> str:
    """Initialize a new Air project."""
    # Placeholder for actual initialization logic
    return f"Air project '{domain_name}' initialized successfully."


@mcp.tool
def air_init_package(pypi_package_name: str) -> str:
    """Initialize a new Air package."""
    # Placeholder for actual package initialization logic
    return f"Air package '{pypi_package_name}' initialized successfully."


if __name__ == "__main__":
    mcp.run()
