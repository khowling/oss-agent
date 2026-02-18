from agent_framework import Agent, MCPStreamableHTTPTool, MCPStdioTool
from agent_framework.openai import OpenAIChatClient

from config import (
    LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_PROVIDER,
    MCP_SERVER_URL, MCP_SERVER_COMMAND, MCP_SERVER_ARGS,
)
from auth import create_token_forwarding_httpx_client, is_auth_enabled

AGENT_INSTRUCTIONS = """You are a helpful assistant.
You have access to tools via MCP servers. Use them when the user's request requires it.
Keep your answers concise and relevant."""


def build_tools() -> list:
    """Build the list of MCP tools based on configuration.

    When Entra ID auth is enabled, uses an httpx client with a request event hook
    that dynamically reads the user's Bearer token from contextvars per-request.
    """
    tools = []
    if MCP_SERVER_URL:
        kwargs = {}
        if is_auth_enabled():
            kwargs["http_client"] = create_token_forwarding_httpx_client()
        tools.append(MCPStreamableHTTPTool(name="lseg-mcp", url=MCP_SERVER_URL, **kwargs))
    if MCP_SERVER_COMMAND:
        args = MCP_SERVER_ARGS.split() if MCP_SERVER_ARGS else []
        tools.append(MCPStdioTool(name="lseg-mcp-stdio", command=MCP_SERVER_COMMAND, args=args))
    return tools


def create_llm_client() -> OpenAIChatClient:
    """Create LLM client supporting both OpenAI and Azure OpenAI (Foundry)."""
    if not LLM_API_KEY:
        raise RuntimeError(
            "LLM_API_KEY is required. Copy .env.example to .env and set your API key."
        )

    if LLM_PROVIDER == "azure":
        from agent_framework.azure import AzureOpenAIChatClient
        return AzureOpenAIChatClient(
            api_key=LLM_API_KEY,
            endpoint=LLM_BASE_URL,
            deployment_name=LLM_MODEL,
            api_version="2024-12-01-preview",
        )

    return OpenAIChatClient(
        api_key=LLM_API_KEY,
        base_url=LLM_BASE_URL,
        model_id=LLM_MODEL,
    )


def create_agent() -> Agent:
    """Create and return the agent with configured LLM and MCP tools."""
    client = create_llm_client()
    tools = build_tools()

    return Agent(
        client=client,
        instructions=AGENT_INSTRUCTIONS,
        name="oss-agent",
        description="LSEG Open Source Agent",
        tools=tools if tools else None,
    )
