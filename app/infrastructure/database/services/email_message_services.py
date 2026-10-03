from app.domain.contracts.email_account.adapters import IGmailProviderAdapter
from app.domain.contracts.email_message.repositories import IEmailMessageRepository
from app.domain.contracts.email_message.servicies import IEmailMessageDispatcherService
from app.domain.entities.email_message.email_message_entity import EmailMessageEntity


class EmailMessageDispatcherService(IEmailMessageDispatcherService):
    def __init__(self, gmail_adapter: IGmailProviderAdapter, email_message_repo: IEmailMessageRepository) -> None:
        self.gmail_adapter=gmail_adapter
        self.email_message_repo=email_message_repo

    async def dispatch(self, message: EmailMessageEntity) -> None:
        if not message.email_account:
            raise Exception('a mensagem a ser enviada nao esta vindulada a nenhum usuario.')

        message.mark_as_processing()
        try:
            await self.gmail_adapter.send_email(email_account_id=message.email_account, to=message.to_address, subject=message.subject, body=message.body)
            message.mark_as_sent()

        except Exception as error:
            print("Error: ", error)
            message.mark_as_failed()
        await self.email_message_repo.save(message)
