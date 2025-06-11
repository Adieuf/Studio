import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import requests

from .copilot_auth import CopilotAuthenticator


class CopilotAgent:
    """Wrapper for Copilot Studio agent Direct Line communication."""

    def __init__(self, auth: CopilotAuthenticator) -> None:
        self.auth = auth
        self.schema_name = os.environ["SCHEMA_NAME"]
        self.agent_id = os.environ["AGENT_ID"]
        self.environment_id = os.environ["ENVIRONMENT_ID"]
        self.resource_app_id = os.environ["RESOURCE_APP_ID"]
        self.api_base = os.environ.get(
            "COPILOT_API_BASE", "https://api.powerva.microsoft.com"
        )
        self._dl_token: Optional[str] = None
        self._dl_expires_on: datetime = datetime.min

    # --- Agent management -------------------------------------------------
    def list_agents(self) -> Dict[str, Any]:
        url = f"{self.api_base}/providers/Microsoft.PowerApps/scopes/admin/environments/{self.environment_id}/agents?api-version=2023-10-01"
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    # --- Direct Line token handling --------------------------------------
    def _token_url(self) -> str:
        return (
            f"{self.api_base}/utilities/tokenprovider/agent/{self.agent_id}"
            f"?environmentId={self.environment_id}&schemaName={self.schema_name}"
        )

    def _refresh_direct_line_token(self) -> None:
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        response = requests.post(self._token_url(), headers=headers, timeout=10)
        response.raise_for_status()
        payload = response.json()
        self._dl_token = payload["token"]
        self._dl_expires_on = datetime.utcnow() + timedelta(
            seconds=int(payload["expires_in"])
        )

    def get_direct_line_token(self) -> str:
        if (
            self._dl_token is None
            or datetime.utcnow() + timedelta(minutes=5) >= self._dl_expires_on
        ):
            self._refresh_direct_line_token()
        assert self._dl_token
        return self._dl_token

    # --- Direct Line conversation helpers --------------------------------
    def start_conversation(self) -> Dict[str, Any]:
        url = "https://directline.botframework.com/v3/directline/conversations"
        headers = {"Authorization": f"Bearer {self.get_direct_line_token()}"}
        response = requests.post(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    def send_activity(
        self, conversation_id: str, activity: Dict[str, Any]
    ) -> Dict[str, Any]:
        url = f"https://directline.botframework.com/v3/directline/conversations/{conversation_id}/activities"
        headers = {"Authorization": f"Bearer {self.get_direct_line_token()}"}
        response = requests.post(url, json=activity, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_activities(
        self, conversation_id: str, watermark: Optional[str] = None
    ) -> Dict[str, Any]:
        url = f"https://directline.botframework.com/v3/directline/conversations/{conversation_id}/activities"
        if watermark:
            url += f"?watermark={watermark}"
        headers = {"Authorization": f"Bearer {self.get_direct_line_token()}"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
