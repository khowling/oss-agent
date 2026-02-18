"""Sample MCP server for local development and testing.

Exposes simple tools that the agent can call:
- calculator: basic arithmetic
- lookup: sample data lookup

Supports optional Entra ID (Azure AD) token validation when
ENTRA_TENANT_ID and MCP_API_CLIENT_ID env vars are set.
"""

import os
import time
import httpx
import jwt
from mcp.server.fastmcp import FastMCP
from mcp.server.auth.provider import TokenVerifier, AccessToken


class EntraTokenVerifier(TokenVerifier):
    """Validates Entra ID JWT access tokens."""

    def __init__(self, tenant_id: str, client_id: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.issuer = f"https://login.microsoftonline.com/{tenant_id}/v2.0"
        self.jwks_uri = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
        self._jwks_client = jwt.PyJWKClient(self.jwks_uri, cache_keys=True)

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=self.issuer,
            )
            return AccessToken(
                token=token,
                client_id=claims.get("azp", ""),
                scopes=claims.get("scp", "").split(),
                expires_at=claims.get("exp", int(time.time()) + 3600),
            )
        except (jwt.InvalidTokenError, Exception):
            return None


# Auth configuration from environment
tenant_id = os.environ.get("ENTRA_TENANT_ID")
mcp_client_id = os.environ.get("MCP_API_CLIENT_ID")

auth_kwargs = {}
if tenant_id and mcp_client_id:
    from mcp.server.auth.settings import AuthSettings
    auth_kwargs["auth"] = AuthSettings(
        issuer_url=f"https://login.microsoftonline.com/{tenant_id}/v2.0",
        resource_server_url="https://mcp.example.com",
    )
    auth_kwargs["token_verifier"] = EntraTokenVerifier(tenant_id, mcp_client_id)
    print(f"MCP auth enabled: tenant={tenant_id}, audience={mcp_client_id}")
else:
    print("MCP auth disabled: set ENTRA_TENANT_ID and MCP_API_CLIENT_ID to enable")

mcp = FastMCP(
    "LSEG Sample Server",
    "A sample MCP server for testing agent tool calls.",
    host="0.0.0.0",
    port=8001,
    **auth_kwargs,
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
