targetScope = 'subscription'

@description('Name prefix for all resources')
param environmentName string

@description('Azure region for all resources')
param location string = 'uksouth'

@description('Azure OpenAI model to deploy')
param openAIModelName string = 'gpt-4o-mini'

@description('Azure OpenAI model version')
param openAIModelVersion string = '2024-07-18'

@description('Azure OpenAI deployment SKU capacity (tokens per minute in thousands)')
param openAICapacity int = 10

var resourceGroupName = 'rg-${environmentName}'
var tags = {
  environment: environmentName
  project: 'oss-agent'
}

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

module containerRegistry 'modules/container-registry.bicep' = {
  name: 'container-registry'
  scope: rg
  params: {
    name: replace('cr${environmentName}', '-', '')
    location: location
    tags: tags
  }
}

module containerAppEnvironment 'modules/container-app-env.bicep' = {
  name: 'container-app-env'
  scope: rg
  params: {
    name: 'cae-${environmentName}'
    location: location
    tags: tags
  }
}

module mcpServer 'modules/container-app.bicep' = {
  name: 'mcp-server'
  scope: rg
  params: {
    name: 'ca-mcp-${environmentName}'
    location: location
    tags: tags
    environmentId: containerAppEnvironment.outputs.id
    registryServer: containerRegistry.outputs.loginServer
    imageName: '${containerRegistry.outputs.loginServer}/oss-agent-mcp:latest'
    targetPort: 8001
    command: ['python', '/app/mcp-servers/sample_server.py']
    envVars: []
    isExternal: false
  }
}

module agent 'modules/container-app.bicep' = {
  name: 'agent'
  scope: rg
  params: {
    name: 'ca-agent-${environmentName}'
    location: location
    tags: tags
    environmentId: containerAppEnvironment.outputs.id
    registryServer: containerRegistry.outputs.loginServer
    imageName: '${containerRegistry.outputs.loginServer}/oss-agent:latest'
    targetPort: 8080
    command: []
    envVars: [
      {
        name: 'LLM_PROVIDER'
        value: 'azure'
      }
      {
        name: 'LLM_API_KEY'
        secretRef: 'llm-api-key'
      }
      {
        name: 'LLM_BASE_URL'
        value: openAI.outputs.endpoint
      }
      {
        name: 'LLM_MODEL'
        value: openAIModelName
      }
      {
        name: 'MCP_SERVER_URL'
        value: 'https://${mcpServer.outputs.fqdn}/mcp'
      }
    ]
    secrets: [
      {
        name: 'llm-api-key'
        value: openAI.outputs.apiKey
      }
    ]
    isExternal: true
  }
}

module openAI 'modules/openai.bicep' = {
  name: 'openai'
  scope: rg
  params: {
    name: 'oai-${environmentName}'
    location: location
    tags: tags
    modelName: openAIModelName
    modelVersion: openAIModelVersion
    capacity: openAICapacity
  }
}

output agentUrl string = 'https://${agent.outputs.fqdn}'
output mcpServerFqdn string = mcpServer.outputs.fqdn
output acrLoginServer string = containerRegistry.outputs.loginServer
output resourceGroupName string = rg.name
