from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.email_account.oauth_dependencies import get_email_account_repository, get_gmail_provider_adapter
from app.application.use_cases.email_message_use_case import ListEmailMessagesUseCase, RegisterEmailMessageUseCase, SendEmailMessageUseCase
from app.domain.contracts.email_account.adapters import IGmailProviderAdapter
from app.domain.contracts.email_account.repositories import IEmailAccountRepository
from app.domain.contracts.email_message.repositories import IEmailMessageRepository
from app.domain.contracts.email_message.servicies import IEmailMessageDispatcherService
from app.infrastructure.database.repositorys.email_message_repository import AdvancedEmailMessageRepository
from app.infrastructure.database.services.email_message_services import EmailMessageDispatcherService
from app.infrastructure.database.sqlite.database import get_session


def get_email_message_repository(session: AsyncSession = Depends(get_session)) -> AdvancedEmailMessageRepository:
    return AdvancedEmailMessageRepository(session=session)


def get_email_message_dispatcher_service(
    gmail_adapter: IGmailProviderAdapter = Depends(get_gmail_provider_adapter),
    email_message_repo: IEmailMessageRepository = Depends(get_email_message_repository)
) -> EmailMessageDispatcherService:
    return EmailMessageDispatcherService(gmail_adapter=gmail_adapter, email_message_repo=email_message_repo)


def get_register_email_message_use_case(
    email_account_repo: IEmailAccountRepository = Depends(get_email_account_repository), 
    email_message_repo: IEmailMessageRepository = Depends(get_email_message_repository), 
    dispatcher: IEmailMessageDispatcherService = Depends(get_email_message_dispatcher_service)
) -> RegisterEmailMessageUseCase:
    return RegisterEmailMessageUseCase(email_message_repo=email_message_repo, email_account_repo=email_account_repo, dispatcher=dispatcher)


def get_send_email_message_use_case(
    email_message_repo: IEmailMessageRepository = Depends(get_email_message_repository), 
    dispatcher: IEmailMessageDispatcherService = Depends(get_email_message_dispatcher_service)
) -> SendEmailMessageUseCase:
    return SendEmailMessageUseCase(email_message_repo=email_message_repo, dispatcher=dispatcher)


def get_list_messages_use_case(
    email_message_repo: IEmailMessageRepository = Depends(get_email_message_repository), 
    email_account_repo: IEmailAccountRepository = Depends(get_email_account_repository), 
) -> ListEmailMessagesUseCase:
    return ListEmailMessagesUseCase(email_message_repo=email_message_repo, email_account_repo=email_account_repo)

RegisterEmailMessageUseCaseDependency = Annotated[RegisterEmailMessageUseCase, Depends(get_register_email_message_use_case)]
SendEmailMessageUseCaseDependency = Annotated[SendEmailMessageUseCase, Depends(get_send_email_message_use_case)]
ListEmailMessagesUSeCaseDependency = Annotated[ListEmailMessagesUseCase, Depends(get_list_messages_use_case)]
