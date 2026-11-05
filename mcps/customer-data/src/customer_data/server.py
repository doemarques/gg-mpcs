from fastmcp import FastMCP

mcp = FastMCP(name="customer-data")


@mcp.tool(description="Echo the provided message.")
def echo(message: str) -> str:
    """Echo the provided message."""
    return message


@mcp.tool(description="Return the sum of two integers.")
def add(a: int, b: int) -> int:
    """Return the sum of two integers."""
    return a + b
