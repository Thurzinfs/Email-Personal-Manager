from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.oauth_use_cases import (
    ConnectEmailAccountUseCase,
    GmailOAuthCallbackUseCase,
)
from app.domain.contracts.email_account.repositories import (
    IEmailAccountRepository,
    IOAuthConnectionRepository,
)
from app.infrastructure.adapters.email_account_adapter import (
    GmailProviderAdapter,
)
from app.infrastructure.clients.gmail_oauth_client import GmailOAuthClient
from app.infrastructure.database.repositorys.email_account_repository import (
    AdvancedEmailAccountRepository,
    AdvancedOAuthConnectionRepository,
)
from app.infrastructure.database.sqlite.database import get_session
from app.infrastructure.security.token_encryptor import (
    ITokenEncryptor,
    TokenEncryptorSecurity,
)
from config.settings import settings


def get_email_account_repository(session: AsyncSession = Depends(get_session)) -> AdvancedEmailAccountRepository:
    return AdvancedEmailAccountRepository(session=session)


def get_oauth_account_repository(
    session: AsyncSession = Depends(get_session),
) -> AdvancedOAuthConnectionRepository:
    return AdvancedOAuthConnectionRepository(session=session)


def get_oauth_client() -> GmailOAuthClient:
    return GmailOAuthClient(
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )


def get_token_encryptor() -> TokenEncryptorSecurity:
    return TokenEncryptorSecurity()


def get_gmail_provider_adapter(
    token_encryptor: ITokenEncryptor = Depends(get_token_encryptor),
    email_account_repo: IEmailAccountRepository = Depends(
        get_email_account_repository
    ),
) -> GmailProviderAdapter:
    return GmailProviderAdapter(
        token_encryptor=token_encryptor, email_account_repo=email_account_repo
    )


def get_oauth_connect_use_case(
    oauth_repo: IOAuthConnectionRepository = Depends(
        get_oauth_account_repository
    ),
    oauth_client: GmailOAuthClient = Depends(get_oauth_client),
) -> ConnectEmailAccountUseCase:
    return ConnectEmailAccountUseCase(
        oauth_repo=oauth_repo, oauth_client=oauth_client
    )


def get_oauth_callback_use_case(
    oauth_repo: IOAuthConnectionRepository = Depends(
        get_oauth_account_repository
    ),
    oauth_client: GmailOAuthClient = Depends(get_oauth_client),
    email_account_repo: IEmailAccountRepository = Depends(
        get_email_account_repository
    ),
    token_encryptor: ITokenEncryptor = Depends(get_token_encryptor),
) -> GmailOAuthCallbackUseCase:
    return GmailOAuthCallbackUseCase(
        oauth_repo=oauth_repo,
        oauth_client=oauth_client,
        email_account_repo=email_account_repo,
        token_encryptor=token_encryptor,
    )


ConnectEmailAccountUseCaseDependency = Annotated[
    ConnectEmailAccountUseCase, Depends(get_oauth_connect_use_case)
]
OAuthCallbackUseCaseDependency = Annotated[
    GmailOAuthCallbackUseCase, Depends(get_oauth_callback_use_case)
]
