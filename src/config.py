import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# Set to "azure" to use Azure OpenAI (Foundry) authentication
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

# MCP Server Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001/mcp")
MCP_SERVER_COMMAND = os.getenv("MCP_SERVER_COMMAND", "")
MCP_SERVER_ARGS = os.getenv("MCP_SERVER_ARGS", "")
