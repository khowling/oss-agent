"""OAuth2 authentication helpers for MCP server access.

Provides:
- Entra ID auth config for frontend MSAL.js flow
- Per-request token context via contextvars
- httpx client factory with dynamic Bearer token injection
"""

import contextvars
import httpx
from config import ENTRA_TENANT_ID, AGENT_CLIENT_ID, MCP_API_CLIENT_ID

# Per-request token context — set by middleware, read by httpx event hook
_request_token: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "_request_token", default=None
)

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


def set_request_token(token: str | None) -> None:
    _request_token.set(token)


def get_request_token() -> str | None:
    return _request_token.get()


def _inject_bearer_token(request: httpx.Request) -> None:
    """httpx event hook that injects the current user's token from contextvars."""
    token = _request_token.get()
    if token:
        request.headers["Authorization"] = f"Bearer {token}"


def create_token_forwarding_httpx_client() -> httpx.AsyncClient:
    """Create an httpx client that dynamically injects the per-request Bearer token.

    The token is read from contextvars at each request time, so a single client
    instance works across all users/requests.
    """
    return httpx.AsyncClient(
        event_hooks={"request": [_inject_bearer_token]},
        timeout=30.0,
    )
