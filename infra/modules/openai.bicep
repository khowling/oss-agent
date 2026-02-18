@description('Name of the Azure OpenAI resource')
param name string

@description('Azure region')
param location string

@description('Resource tags')
param tags object = {}

@description('Model to deploy')
param modelName string

@description('Model version')
param modelVersion string

@description('Deployment capacity (TPM in thousands)')
param capacity int = 10

resource openAI 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: name
  location: location
  tags: tags
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: name
    publicNetworkAccess: 'Enabled'
  }
}

resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: openAI
  name: modelName
  sku: {
    name: 'Standard'
    capacity: capacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: modelName
      version: modelVersion
    }
  }
}

output endpoint string = '${openAI.properties.endpoint}openai/deployments/${modelName}'
output apiKey string = openAI.listKeys().key1
output name string = openAI.name
