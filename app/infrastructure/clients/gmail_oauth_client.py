from datetime import timezone
from typing import Any, Tuple

from google_auth_oauthlib.flow import Flow

import requests

import os


if os.getenv('ENVIRONMENT', 'development') == 'development':
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
]


class GmailOAuthClient:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def _build_flow(self) -> Flow:
        client_config = {
            'web': {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }

        return Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=self.redirect_uri
        )

    def generate_authorization_uri(self) -> Tuple[str, str, str]:
        flow = self._build_flow()
        auth, state = flow.authorization_url(access_type='offline', prompt='consent')

        assert isinstance(auth, str)
        assert isinstance(state, str)
        assert isinstance(flow.code_verifier, str)

        return auth, state, flow.code_verifier

    def exchange_code_for_tokens(self, code: str, code_verifier: str) -> dict[str, Any]:
        flow = self._build_flow()
        flow.code_verifier = code_verifier
        flow.fetch_token(code=code)
        creds = flow.credentials
        return {
            "access_token": creds.token,
            "refresh_token": creds.refresh_token,
            "expires_at": creds.expiry.replace(tzinfo=timezone.utc) if creds.expiry else None,
        }

    def get_user_email(self, access_token: str) -> str:
        response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()
        return response.json().get("email", "")
