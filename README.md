# Copilot Chat Sample

Minimal web app for chatting with a Copilot Studio agent.

## Setup

```bash
az deployment sub create \
  --location eastus \
  --template-file infra/main.bicep \
  --parameters appName=mycopilot
```

Create a `.env` file with your tenant and agent info.
Run the API locally with `uvicorn backend.main:app --port 8000`.

## Diagram
```mermaid
sequenceDiagram
    participant B as Browser
    participant A as API
    participant C as Copilot Studio
    B->>A: Request Direct Line token
    A->>C: AAD token\nexchange
    C-->>A: Direct Line token
    A-->>B: Token
    B->>A: Activities
    A->>C: Proxy
    C-->>A: Activities
    A-->>B: Activities
```
