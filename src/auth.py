"""OAuth2 authentication helpers for MCP server access.

Provides:
- MSAL-based token acquisition for Entra ID
- Auth endpoints for the agent server (login redirect, callback, token)
- httpx client factory with Bearer token injection
"""

import httpx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from config import ENTRA_TENANT_ID, AGENT_CLIENT_ID, MCP_API_CLIENT_ID


# In-memory token store keyed by session
_token_store: dict[str, str] = {}

AUTHORITY = f"https://login.microsoftonline.com/{ENTRA_TENANT_ID}"
SCOPE = f"api://{MCP_API_CLIENT_ID}/MCP.Access"


def is_auth_enabled() -> bool:
    return bool(ENTRA_TENANT_ID and AGENT_CLIENT_ID and MCP_API_CLIENT_ID)


def get_auth_config() -> dict:
    """Return auth config for the frontend to initiate PKCE flow."""
    return {
        "enabled": is_auth_enabled(),
        "authority": AUTHORITY,
        "clientId": AGENT_CLIENT_ID,
        "scope": SCOPE,
        "tenantId": ENTRA_TENANT_ID,
    }


def store_token(session_id: str, token: str) -> None:
    _token_store[session_id] = token


def get_token(session_id: str) -> str | None:
    return _token_store.get(session_id)


def create_authenticated_httpx_client(token: str) -> httpx.AsyncClient:
    """Create an httpx client that attaches Bearer token to all requests."""
    return httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"},
        timeout=30.0,
    )
