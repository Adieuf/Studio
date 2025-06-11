// Deploy App Service, Key Vault, and Managed Identity for Copilot Chat
param prefix string
param environment string
param clientSecretName string = 'CLIENT-SECRET'
param location string = resourceGroup().location

var rgName = 'rg-${prefix}-${environment}-${location}'

resource kv 'Microsoft.KeyVault/vaults@2022-07-01' = {
  name: '${prefix}-kv-${environment}'
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    accessPolicies: []
  }
}

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${prefix}-id-${environment}'
  location: location
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${prefix}-ai-${environment}'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
}

resource plan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: '${prefix}-plan-${environment}'
  location: location
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
}

resource web 'Microsoft.Web/sites@2022-03-01' = {
  name: '${prefix}-api-${environment}'
  location: location
  kind: 'app'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identity.id}': {}
    }
  }
  properties: {
    serverFarmId: plan.id
    siteConfig: {
      appSettings: [
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsights.properties.InstrumentationKey
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsights.properties.ConnectionString
        }
        {
          name: 'KEY_VAULT_URI'
          value: kv.properties.vaultUri
        }
        {
          name: 'CLIENT_SECRET_NAME'
          value: clientSecretName
        }
        {
          name: 'AZURE_CLIENT_ID'
          value: identity.properties.clientId
        }
      ]
      cors: {
        allowedOrigins: [ 'https://localhost' ]
      }
    }
  }
}

resource swa 'Microsoft.Web/staticSites@2022-03-01' = {
  name: '${prefix}-swa-${environment}'
  location: location
  sku: {
    name: 'Free'
    tier: 'Free'
  }
}

// Grant web app access to Key Vault
resource kvAccess 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(web.id, 'KeyVaultAccess')
  scope: kv
  properties: {
    principalId: identity.properties.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b86a8fe4-44ce-4948-aee5-eccb2c155cd7')
  }
  dependsOn: [ identity ]
}

output webAppUrl string = 'https://${web.properties.defaultHostName}'
output staticWebUrl string = 'https://${swa.properties.defaultHostname}'
