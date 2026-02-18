@description('Name of the container registry')
param name string

@description('Azure region')
param location string

@description('Resource tags')
param tags object = {}

resource acr 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
  }
  identity: {
    type: 'SystemAssigned'
  }
}

output loginServer string = acr.properties.loginServer
output name string = acr.name
output identityId string = acr.identity.principalId
