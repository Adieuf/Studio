"""Helper functions for Azure AD authentication."""

from datetime import datetime, timedelta
from typing import Dict

import requests


class AADTokenProvider:
    """Fetches application tokens from Azure AD using client credentials."""

    def __init__(self, tenant_id: str, client_id: str, client_secret: str) -> None:
        self._tenant_id = tenant_id
        self._client_id = client_id
        self._client_secret = client_secret
        self._token: str | None = None
        self._expires: datetime | None = None

    def _request_token(self, scope: str) -> Dict[str, str]:
        url = f"https://login.microsoftonline.com/{self._tenant_id}/oauth2/v2.0/token"
        payload = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "scope": scope,
            "grant_type": "client_credentials",
        }
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_token(self, scope: str) -> str:
        """Return a valid AAD access token for the given scope."""
        if self._token and self._expires and datetime.utcnow() < self._expires:
            return self._token

        token_data = self._request_token(scope)
        self._token = token_data["access_token"]
        self._expires = datetime.utcnow() + timedelta(
            seconds=int(token_data.get("expires_in", 3600)) - 60
        )
        return self._token
