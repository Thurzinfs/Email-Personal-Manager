from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.domain.contracts.email_account.adapters import IGmailProviderAdapter
from app.domain.contracts.email_account.repositories import IEmailAccountRepository, IOAuthConnectionRepository
from app.domain.contracts.user.repositories import IUserRepository
from app.domain.entities.email_account.emai_account_entity import EmailAccountEntity, OAuthConnectionEntity
from app.domain.exceptions.gmail_account_exceptions import GmailAccountNotConnectedException, InvalidOAuthStateException
from app.domain.exceptions.user_exceptions import UserNotFoundException
from app.infrastructure.clients.gmail_oauth_client import GmailOAuthClient
from app.infrastructure.security.token_encryptor import ITokenEncryptor


class ConnectEmailAccountUseCase:
    def __init__(self, oauth_repo: IOAuthConnectionRepository, oauth_client: GmailOAuthClient) -> None:
        self.oauth_repo=oauth_repo
        self.oauth_client=oauth_client

    async def execute(self, user_id: UUID) -> str:
        auth_url, state, code_verifier = self.oauth_client.generate_authorization_uri()

        att = OAuthConnectionEntity(
            user_id=user_id,
            state=state,
            code_verifier=code_verifier,
            expire_at=datetime.now(timezone.utc) + timedelta(minutes=10)
        )
        await self.oauth_repo.save(att)
        return auth_url


class GmailOAuthCallbackUseCase:
    def __init__(self, oauth_repo: IOAuthConnectionRepository, oauth_client: GmailOAuthClient, email_account_repo: IEmailAccountRepository, token_encryptor: ITokenEncryptor) -> None:
        self.oauth_repo = oauth_repo
        self.oauth_client = oauth_client
        self.email_account_repo = email_account_repo
        self.token_encryptor = token_encryptor

    async def execute(self, code: str, state: str) -> None:
        connection = await self.oauth_repo.find_by_state(state)
        print('connection: ', connection)

        if not connection or connection.is_expired():
            raise InvalidOAuthStateException()

        await self.oauth_repo.delete_by_state(state)

        tokens = self.oauth_client.exchange_code_for_tokens(
            code=code, 
            code_verifier=connection.code_verifier
        )

        if not connection.user_id:
            raise UserNotFoundException()

        existing_account = await self.email_account_repo.find_by_user_id(connection.user_id)

        encrypted_access = self.token_encryptor.encrypt(tokens['access_token']) 
        encrypted_refresh = self.token_encryptor.encrypt(tokens['refresh_token'])

        email_address = self.oauth_client.get_user_email(tokens['access_token'])

        if existing_account:
            existing_account.access_token = encrypted_access
            existing_account.refresh_token = encrypted_refresh
            existing_account.token_expire_at = tokens['expires_at']
            existing_account.connected = True
            account = existing_account

        else:
            account = EmailAccountEntity(
                user=connection.user_id,
                token_expire_at=tokens['expires_at'],
                access_token=encrypted_access,
                refresh_token=encrypted_refresh,
                provider='gmail',
                scopes=['gmail.readonly', 'gmail.send'],
                connected=True,
                connected_at=datetime.now(timezone.utc),
                email_address=email_address
            )

        await self.email_account_repo.save(account)


class DisconectEmailAccountUseCase:
    def __init__(self, email_account_repo: IEmailAccountRepository, gmail_adapter: IGmailProviderAdapter) -> None:
        self.email_account_repo=email_account_repo
        self.gmail_adapter=gmail_adapter

    async def execute(self, user: UUID) -> None:
        account = await self.email_account_repo.find_by_user_id(user)
        if not account:
            raise GmailAccountNotConnectedException()

        try:
            await self.gmail_adapter.revoke(account.id)

        except Exception:
            pass

        account.disconnect()
        await self.email_account_repo.save(account)
        