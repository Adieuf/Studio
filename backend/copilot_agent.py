"""Wrapper around Copilot Studio Agent APIs."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import requests

from .copilot_auth import AADTokenProvider


class CopilotAgent:
    """Utility to interact with a Copilot Studio agent via Direct Line."""

    def __init__(
        self,
        aad_provider: AADTokenProvider,
        agent_id: str,
        environment_id: str,
        resource_app_id: str,
        directline_endpoint: str,
        token_endpoint: str,
    ) -> None:
        self._aad_provider = aad_provider
        self._agent_id = agent_id
        self._environment_id = environment_id
        self._resource_app_id = resource_app_id
        self._directline_endpoint = directline_endpoint.rstrip("/")
        self._token_endpoint = token_endpoint
        self._dl_token: str | None = None
        self._dl_expiry: datetime | None = None

    def _fetch_directline_token(self) -> str:
        scope = f"api://{self._resource_app_id}/.default"
        aad_token = self._aad_provider.get_token(scope)
        headers = {"Authorization": f"Bearer {aad_token}"}
        params = {
            "agentId": self._agent_id,
            "environmentId": self._environment_id,
        }
        response = requests.get(
            self._token_endpoint, headers=headers, params=params, timeout=10
        )
        response.raise_for_status()
        data = response.json()
        self._dl_token = data["token"]
        self._dl_expiry = datetime.utcnow() + timedelta(
            seconds=int(data.get("expires_in", 1800)) - 60
        )
        return self._dl_token

    def get_directline_token(self) -> str:
        """Return a valid Direct Line token, refreshing when needed."""
        if self._dl_token and self._dl_expiry and datetime.utcnow() < self._dl_expiry:
            return self._dl_token
        return self._fetch_directline_token()

    def start_conversation(self) -> Dict[str, Any]:
        """Start a Direct Line conversation."""
        token = self.get_directline_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{self._directline_endpoint}/v3/directline/conversations"
        response = requests.post(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    def send_activity(
        self, conversation_id: str, activity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send an activity to the conversation."""
        token = self.get_directline_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{self._directline_endpoint}/v3/directline/conversations/{conversation_id}/activities"
        response = requests.post(url, headers=headers, json=activity, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_activities(
        self, conversation_id: str, watermark: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieve activities from the conversation."""
        token = self.get_directline_token()
        headers = {"Authorization": f"Bearer {token}"}
        params = {"watermark": watermark} if watermark else {}
        url = f"{self._directline_endpoint}/v3/directline/conversations/{conversation_id}/activities"
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def list_agents(self) -> Dict[str, Any]:
        """Example method to list agents using the AAD token."""
        scope = f"api://{self._resource_app_id}/.default"
        aad_token = self._aad_provider.get_token(scope)
        headers = {"Authorization": f"Bearer {aad_token}"}
        response = requests.get(
            f"{self._directline_endpoint}/v1/agents",
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
