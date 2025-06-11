param appName string
param location string = resourceGroup().location
param environment string = 'prod'

var prefix = '${appName}-${environment}'

resource plan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: 'plan-${prefix}'
  location: location
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
}

resource app 'Microsoft.Web/sites@2022-09-01' = {
  name: 'app-${prefix}'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.10'
    }
  }
}

resource ai 'Microsoft.Insights/components@2020-02-02' = {
  name: 'ai-${prefix}'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
}

resource kv 'Microsoft.KeyVault/vaults@2022-07-01' = {
  name: 'kv-${prefix}'
  location: location
  properties: {
    enableSoftDelete: true
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    accessPolicies: [
      {
        tenantId: subscription().tenantId
        objectId: app.identity.principalId
        permissions: {
          secrets: ['get']
        }
      }
    ]
  }
}

resource secret 'Microsoft.KeyVault/vaults/secrets@2022-07-01' = {
  name: '${kv.name}/CLIENT-SECRET'
  properties: {
    value: 'REPLACE_ME'
  }
}

// Optional Static Web App for frontend
resource swa 'Microsoft.Web/staticSites@2022-03-01' = {
  name: 'swa-${prefix}'
  location: location
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    buildProperties: {
      appLocation: 'frontend'
    }
  }
  dependsOn: [app]
}

output webAppUrl string = app.properties.defaultHostName
