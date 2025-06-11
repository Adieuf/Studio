import os
from datetime import datetime, timedelta
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()


class CopilotAuthenticator:
    """Helper for acquiring Azure AD application tokens."""

    def __init__(self) -> None:
        self.tenant_id = os.environ["TENANT_ID"]
        self.client_id = os.environ["CLIENT_ID"]
        self.client_secret = os.environ.get("CLIENT_SECRET")
        self.scope = os.environ.get("SCOPE", "https://graph.microsoft.com/.default")
        self.token_endpoint = (
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        )
        self._token: Optional[str] = None
        self._expires_on: datetime = datetime.min

    def _request_token(self) -> None:
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.scope,
            "grant_type": "client_credentials",
        }
        response = requests.post(self.token_endpoint, data=data, timeout=10)
        response.raise_for_status()
        payload = response.json()
        self._token = payload["access_token"]
        self._expires_on = datetime.utcnow() + timedelta(
            seconds=int(payload["expires_in"])
        )

    def get_token(self) -> str:
        """Return a cached Azure AD token, refreshing if needed."""
        if (
            self._token is None
            or datetime.utcnow() + timedelta(minutes=5) >= self._expires_on
        ):
            self._request_token()
        assert self._token
        return self._token
