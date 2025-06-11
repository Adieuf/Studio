"""FastAPI application exposing chat endpoints."""

from __future__ import annotations

import os
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from .copilot_auth import AADTokenProvider
from .copilot_agent import CopilotAgent

app = FastAPI(title="Copilot Studio Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_methods=["POST"],
    allow_headers=["*"],
)


def _load_client_secret() -> str:
    """Retrieve the application secret from Key Vault or environment."""
    vault_uri = os.getenv("KEY_VAULT_URI")
    secret_name = os.getenv("CLIENT_SECRET_NAME", "CLIENT-SECRET")
    if vault_uri:
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=vault_uri, credential=credential)
        return client.get_secret(secret_name).value
    return os.getenv("CLIENT_SECRET", "")


aad_provider = AADTokenProvider(
    tenant_id=os.getenv("TENANT_ID", ""),
    client_id=os.getenv("CLIENT_ID", ""),
    client_secret=_load_client_secret(),
)

agent = CopilotAgent(
    aad_provider=aad_provider,
    agent_id=os.getenv("AGENT_ID", ""),
    environment_id=os.getenv("ENVIRONMENT_ID", ""),
    resource_app_id=os.getenv("RESOURCE_APP_ID", ""),
    directline_endpoint=os.getenv(
        "DIRECTLINE_ENDPOINT", "https://directline.botframework.com"
    ),
    token_endpoint=os.getenv("TOKEN_ENDPOINT", ""),
)


@app.post("/api/chat/token")
async def get_token() -> Dict[str, str]:
    """Return a Direct Line token for Web Chat."""
    try:
        token = agent.get_directline_token()
        return {"token": token}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/chat/conversations")
async def start_conversation() -> Dict[str, Any]:
    """Start a Direct Line conversation."""
    try:
        return agent.start_conversation()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/chat/conversations/{conversation_id}/activities")
async def post_activity(conversation_id: str, request: Request) -> Dict[str, Any]:
    """Proxy activity to the agent."""
    try:
        activity = await request.json()
        return agent.send_activity(conversation_id, activity)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/chat/conversations/{conversation_id}/activities")
async def get_activities(
    conversation_id: str, watermark: str | None = None
) -> Dict[str, Any]:
    """Retrieve activities from the agent."""
    try:
        return agent.get_activities(conversation_id, watermark)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
