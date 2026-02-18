import uvicorn
from agent_framework.devui import DevServer
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from agent import create_agent
from auth import get_auth_config, store_token


agent = create_agent()


async def auth_config(request: Request) -> JSONResponse:
    """Return Entra ID config for frontend OAuth flow."""
    return JSONResponse(get_auth_config())


async def auth_token(request: Request) -> JSONResponse:
    """Store access token from frontend after user login."""
    body = await request.json()
    session_id = body.get("session_id", "default")
    token = body.get("access_token", "")
    store_token(session_id, token)
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    server = DevServer(port=8080, host="0.0.0.0")
    server._pending_entities = [agent]
    app = server.get_app()

    # Mount auth API routes
    auth_routes = [
        Route("/api/auth/config", auth_config, methods=["GET"]),
        Route("/api/auth/token", auth_token, methods=["POST"]),
    ]
    for route in auth_routes:
        app.routes.insert(0, route)

    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
