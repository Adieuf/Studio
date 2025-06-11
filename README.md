# Copilot Studio Chat

Minimal custom chat application for Copilot Studio.

## Sequence Diagram
```mermaid
sequenceDiagram
    Browser->>API: POST /api/chat/conversations
    API->>Copilot Studio: exchange AAD token for DL token
    Copilot Studio-->>API: Direct Line token
    API-->>Browser: conversation info
    Browser->>API: POST/GET /api/chat/conversations/{id}/activities
    API->>Copilot Studio: proxy messages
    Copilot Studio-->>API: activities
    API-->>Browser: activities
```

## Local Development

Set the following environment variables:

```
TENANT_ID=
CLIENT_ID=
AGENT_ID=
ENVIRONMENT_ID=
RESOURCE_APP_ID=
TOKEN_ENDPOINT=
DIRECTLINE_ENDPOINT=https://directline.botframework.com
KEY_VAULT_URI=
CLIENT_SECRET_NAME=CLIENT-SECRET
```

The Bicep deployment creates an Azure Key Vault and a managed identity for the
API. Store the `CLIENT_SECRET` for your Azure AD application in the vault using
the name specified by `CLIENT_SECRET_NAME`. The `KEY_VAULT_URI` environment
variable should point at this vault when running locally.

Install dependencies and run:

```bash
pip install fastapi uvicorn requests python-dotenv azure-identity azure-keyvault-secrets
python -m uvicorn backend.main:app --reload
```

## Deployment

```bash
az deployment sub create \
  --location <region> \
  --template-file infra/main.bicep \
  --parameters prefix=<app> environment=prod
```
