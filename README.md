# OSS Agent

A self-hosted AI agent built with [Microsoft Agent Framework](https://github.com/microsoft/agent-framework), 
connecting to any OpenAI-compatible LLM endpoint and consuming tools via [MCP](https://modelcontextprotocol.io/) servers.

## Architecture

See [docs/architecture-options.md](docs/architecture-options.md) for architecture diagrams.

## Quick Start

### Prerequisites

- Python 3.12+
- An OpenAI-compatible API key (OpenAI, Azure OpenAI, GitHub Models, etc.)

### 1. Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your LLM API key and endpoint
```

### 3. Run the Sample MCP Server (optional)

```bash
python mcp-servers/sample_server.py
```

This starts a sample MCP server on `http://localhost:8001` with two tools:
- `calculator` — evaluate arithmetic expressions
- `lookup_instrument` — look up financial instrument data

### 4. Run the Agent

```bash
cd src
python main.py
```

The agent starts with the Dev UI at **http://localhost:8080**. Open it in your browser to chat with the agent.

## Docker

### Build and run with docker-compose

```bash
cp .env.example .env
# Edit .env with your LLM API key
docker compose up --build
```

This starts both the agent (port 8080) and the sample MCP server (port 8001).

## Configuration

All configuration is via environment variables (or `.env` file):

| Variable | Description | Default |
|---|---|---|
| `LLM_PROVIDER` | `openai` or `azure` | `openai` |
| `LLM_API_KEY` | API key for your LLM provider | (required) |
| `LLM_BASE_URL` | Base URL of the API | `https://api.openai.com/v1` |
| `LLM_MODEL` | Model / deployment name | `gpt-4o-mini` |
| `MCP_SERVER_URL` | URL of an MCP server (HTTP transport) | `http://localhost:8001/mcp` |
| `MCP_SERVER_COMMAND` | Command to run an MCP server (stdio transport) | (optional) |
| `MCP_SERVER_ARGS` | Arguments for the stdio MCP server command | (optional) |

## Deploy to Azure

### Prerequisites

- Azure CLI (`az`) installed and logged in
- A GitHub repository with this code
- An Azure subscription

### 1. Deploy infrastructure (Bicep)

```bash
az deployment sub create \
  --location uksouth \
  --template-file infra/main.bicep \
  --parameters infra/main.bicepparam
```

This creates:
- **Resource Group** with all resources
- **Azure Container Registry** for Docker images
- **Azure Container App Environment** with Log Analytics
- **Azure Container App** for the agent (port 8080, external)
- **Azure Container App** for the MCP server (port 8001, internal)
- **Azure OpenAI** resource with model deployment

### 2. Push images to ACR

```bash
ACR_NAME=$(az deployment sub show --name main --query properties.outputs.acrLoginServer.value -o tsv)
az acr login --name $ACR_NAME

docker build -t $ACR_NAME/oss-agent:latest .
docker push $ACR_NAME/oss-agent:latest

docker build -t $ACR_NAME/oss-agent-mcp:latest .
docker push $ACR_NAME/oss-agent-mcp:latest
```

### 3. CI/CD with GitHub Actions

The workflow at `.github/workflows/deploy.yml` automates build and deploy on push to `main`.

**Required GitHub Secrets:**
| Secret | Description |
|---|---|
| `AZURE_CLIENT_ID` | Service principal / federated identity client ID |
| `AZURE_TENANT_ID` | Azure AD tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |

Set up [OIDC federation](https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure) for passwordless authentication.

## Project Structure

```
oss-agent/
├── src/
│   ├── main.py               # Entrypoint — starts agent with Dev UI
│   ├── agent.py              # Agent definition (LLM, tools, instructions)
│   └── config.py             # Environment configuration loader
├── mcp-servers/
│   └── sample_server.py      # Sample MCP server for testing
├── infra/
│   ├── main.bicep            # Main Bicep template (subscription-scoped)
│   ├── main.bicepparam       # Bicep parameters
│   └── modules/
│       ├── container-app.bicep
│       ├── container-app-env.bicep
│       ├── container-registry.bicep
│       └── openai.bicep
├── .github/
│   └── workflows/
│       └── deploy.yml        # CI/CD pipeline
├── docs/
│   └── architecture-options.md
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## License

MIT
