import asyncio
import base64
from email.message import EmailMessage
import os
from typing import Any
from uuid import UUID

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from app.domain.contracts.email_account.adapters import IGmailProviderAdapter
from app.domain.contracts.email_account.repositories import IEmailAccountRepository
from app.infrastructure.security.token_encryptor import ITokenEncryptor


class GmailProviderAdapter(IGmailProviderAdapter):
    def __init__(self, token_encryptor: ITokenEncryptor, email_account_repo: IEmailAccountRepository) -> None:
        self.token_encryptor=token_encryptor
        self.email_account_repo=email_account_repo

    async def get_service(self, email_account_id: UUID):
        account = await self.email_account_repo.find_by_id(email_account_id)
        if not account:
            raise ValueError(f"Conta de e-mail com ID '{email_account_id}' não foi encontrada.")

        creds = Credentials(
            token=self.token_encryptor.decrypt(account.access_token),
            refresh_token=self.token_encryptor.decrypt(account.refresh_token),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET')
        )

        if creds.expired:
            creds.refresh(Request())
            account.refresh(
                new_access=self.token_encryptor.encrypt(creds.token),
                new_expire=creds.expiry  # type: ignore
            )
            await self.email_account_repo.save(account)

        return build('gmail', 'v1', credentials=creds)

    async def send_email(self, email_account_id: UUID, to: str, subject: str, body: Any):
        service = await self.get_service(email_account_id)

        message = EmailMessage()
        message.set_content(body)
        message['To'] = to
        message['Subject'] = subject
        encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()

        def _send():
            return service.users().messages().send(
                userId='me', 
                body={'raw': encoded}
            ).execute()

        sent = await asyncio.to_thread(_send)

        return sent['id']
