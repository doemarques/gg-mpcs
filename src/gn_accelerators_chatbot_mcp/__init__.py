from .server import mcp


def main() -> None:
    mcp.run(transport="http", host="0.0.0.0", port=8000)
