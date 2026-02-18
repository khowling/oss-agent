import os
import uvicorn
from agent_framework.devui import DevServer
from starlette.requests import Request
from starlette.responses import JSONResponse, FileResponse
from starlette.routing import Route

from agent import create_agent
from auth import get_auth_config, is_auth_enabled


async def auth_config(request: Request) -> JSONResponse:
    """Return Entra ID config for frontend MSAL.js OAuth flow."""
    return JSONResponse(get_auth_config())


async def login_page(request: Request) -> FileResponse:
    """Serve the MSAL.js login page."""
    login_path = os.path.join(os.path.dirname(__file__), "static", "login.html")
    return FileResponse(login_path, media_type="text/html")


# Create agent without auth — token is injected per-request via middleware
agent = create_agent()


if __name__ == "__main__":
    # When auth is enabled, set DEVUI_AUTH_TOKEN so the DevUI shows auth_required: true
    # and sends the user's token as Bearer header on all API requests.
    # We use a placeholder value — the actual validation happens at the MCP server.
    if is_auth_enabled():
        os.environ["AUTH_REQUIRED"] = "true"
        os.environ["DEVUI_AUTH_TOKEN"] = "entra-id-delegated"

    server = DevServer(port=8080, host="0.0.0.0")
    server._pending_entities = [agent]
    app = server.get_app()

    # Mount custom routes before framework routes
    custom_routes = [
        Route("/api/auth/config", auth_config, methods=["GET"]),
        Route("/login", login_page, methods=["GET"]),
    ]
    for route in custom_routes:
        app.routes.insert(0, route)

    # When auth is enabled, replace the token validation middleware.
    # The DevUI's built-in middleware does static token comparison, but we want
    # to accept any Entra ID token (validated downstream by the MCP server).
    if is_auth_enabled():
        from starlette.middleware.base import BaseHTTPMiddleware

        class EntraAuthMiddleware(BaseHTTPMiddleware):
            """Accept any Bearer token and forward it to MCP via contextvars."""

            SKIP_PATHS = {"/health", "/meta", "/", "/login", "/api/auth/config"}

            async def dispatch(self, request, call_next):
                from auth import set_request_token

                path = request.url.path
                if (
                    request.method == "OPTIONS"
                    or path in self.SKIP_PATHS
                    or path.startswith("/assets")
                ):
                    return await call_next(request)

                auth_header = request.headers.get("Authorization", "")
                if not auth_header.startswith("Bearer "):
                    return JSONResponse(
                        status_code=401,
                        content={"error": {"message": "Bearer token required", "code": "missing_token"}},
                    )

                token = auth_header.removeprefix("Bearer ").strip()
                set_request_token(token)
                return await call_next(request)

        # Remove the framework's built-in auth middleware and add ours
        # The framework adds auth as the last middleware in the stack
        app.middleware_stack = None  # Force rebuild
        # Clear existing user middleware that does static token comparison
        app.user_middleware = [
            m for m in app.user_middleware
            if "auth_middleware" not in str(m)
        ]
        app.add_middleware(EntraAuthMiddleware)

    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
