"""
Authentication module for Microsoft Partner Center API
"""

import requests
from typing import Dict, Any


class AuthContext:
    """Handles authentication with Microsoft Partner Center API"""

    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = None

    def get_access_token(self) -> str:
        """Get or refresh the access token"""
        if self._access_token is None:
            self._access_token = self._authenticate()
        return self._access_token

    def _authenticate(self) -> str:
        """Authenticate with Azure AD and get access token"""
        auth_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://api.partner.microsoft.com/.default",
            "grant_type": "client_credentials",
        }

        response = requests.post(auth_url, data=payload)
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data["access_token"]
        else:
            raise Exception(f"Authentication failed: {response.text}")

    def get_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests"""
        return {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json",
        }
