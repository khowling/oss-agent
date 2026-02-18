"""Sample MCP server for local development and testing.

Exposes simple tools that the agent can call:
- calculator: basic arithmetic
- lookup: sample data lookup
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "LSEG Sample Server",
    "A sample MCP server for testing agent tool calls.",
    host="0.0.0.0",
    port=8001,
)


@mcp.tool()
def calculator(expression: str) -> str:
    """Evaluate a simple arithmetic expression. Supports +, -, *, / and parentheses."""
    allowed = set("0123456789+-*/.() ")
    if not all(c in allowed for c in expression):
        return "Error: expression contains invalid characters"
    try:
        result = eval(expression)  # noqa: S307
        return str(result)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def lookup_instrument(symbol: str) -> str:
    """Look up basic information about a financial instrument by its ticker symbol."""
    instruments = {
        "AAPL": {"name": "Apple Inc.", "exchange": "NASDAQ", "currency": "USD", "sector": "Technology"},
        "MSFT": {"name": "Microsoft Corp.", "exchange": "NASDAQ", "currency": "USD", "sector": "Technology"},
        "LSEG.L": {"name": "London Stock Exchange Group", "exchange": "LSE", "currency": "GBP", "sector": "Financials"},
        "BARC.L": {"name": "Barclays PLC", "exchange": "LSE", "currency": "GBP", "sector": "Financials"},
    }
    info = instruments.get(symbol.upper())
    if info:
        return f"{symbol.upper()}: {info['name']} | Exchange: {info['exchange']} | Currency: {info['currency']} | Sector: {info['sector']}"
    return f"Instrument '{symbol}' not found. Available: {', '.join(instruments.keys())}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
