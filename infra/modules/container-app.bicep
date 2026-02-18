@description('Name of the Container App')
param name string

@description('Azure region')
param location string

@description('Resource tags')
param tags object = {}

@description('Container App Environment resource ID')
param environmentId string

@description('Target port for the container')
param targetPort int

@description('Environment variables')
param envVars array = []

@description('Secrets')
param secrets array = []

@description('Whether the app is externally accessible')
param isExternal bool = false

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    managedEnvironmentId: environmentId
    configuration: {
      ingress: {
        external: isExternal
        targetPort: targetPort
        transport: 'auto'
      }
      secrets: secrets
    }
    template: {
      containers: [
        {
          name: name
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: envVars
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 3
      }
    }
  }
  identity: {
    type: 'SystemAssigned'
  }
}

output fqdn string = containerApp.properties.configuration.ingress.fqdn
output name string = containerApp.name
