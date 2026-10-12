from app.application.use_cases.email_message_use_case import ListEmailMessagesToSendUseCase, SendEmailMessageUseCase
from app.infrastructure.adapters.email_account_adapter import GmailProviderAdapter
from app.infrastructure.database.repositorys.email_account_repository import AdvancedEmailAccountRepository
from app.infrastructure.database.repositorys.email_message_repository import AdvancedEmailMessageRepository
from app.infrastructure.database.services.email_message_services import EmailMessageDispatcherService
from app.infrastructure.database.sqlite.database import config
from app.infrastructure.security.token_encryptor import TokenEncryptorSecurity


async def check_and_send_messages():
    print('verificando')
    async with config.get_session() as session:
        message_repo = AdvancedEmailMessageRepository(session=session)
        account_repo = AdvancedEmailAccountRepository(session=session)
        adapter = GmailProviderAdapter(
            email_account_repo=account_repo,
            token_encryptor=TokenEncryptorSecurity()
        )
        dispatcher = EmailMessageDispatcherService(email_message_repo=message_repo, gmail_adapter=adapter)

        list_messages_use_case = ListEmailMessagesToSendUseCase(message_repo=message_repo)
        sent_message_use_case = SendEmailMessageUseCase(email_message_repo=message_repo, dispatcher=dispatcher)

        messages = await list_messages_use_case.execute()
        for message in messages:
            await sent_message_use_case.execute(message.id)
