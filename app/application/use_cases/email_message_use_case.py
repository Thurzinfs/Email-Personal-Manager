from uuid import UUID

from app.application.dtos.email_messages_dtos import EmailMessageInDTO, EmailMessageOutDTO
from app.domain.contracts.email_account.repositories import IEmailAccountRepository
from app.domain.contracts.email_message.repositories import IEmailMessageRepository
from app.domain.contracts.email_message.servicies import IEmailMessageDispatcherService
from app.domain.entities.email_message.email_message_entity import EmailMessageEntity
from app.domain.exceptions.user_exceptions import UserNotFoundException
from app.domain.value_objects.scheduled_at_vo import ScheduledAtVO


class RegisterEmailMessageUseCase:
    def __init__(self, email_account_repo: IEmailAccountRepository, email_message_repo: IEmailMessageRepository, dispatcher: IEmailMessageDispatcherService) -> None:
        self.email_account_repo = email_account_repo
        self.email_message_repo = email_message_repo
        self.dispatcher = dispatcher

    async def execute(self, user: UUID, dto: EmailMessageInDTO):
        account = await self.email_account_repo.find_by_user_id(user)
        if not account:
            raise UserNotFoundException()

        sent_now = dto.scheduled_at is None

        message = EmailMessageEntity(
            to_address=dto.to,
            subject=dto.subject,
            body=dto.body,
            scheduled_at=ScheduledAtVO(value=dto.scheduled_at) if dto.scheduled_at else None,
            email_account=account.user
        )
        await self.email_message_repo.save(message)

        if sent_now:
            await self.dispatcher.dispatch(message)

        return EmailMessageOutDTO.from_domain(message)


class SendEmailMessageUseCase:
    def __init__(self, email_message_repo: IEmailMessageRepository, dispatcher: IEmailMessageDispatcherService) -> None:
        self.email_message_repo=email_message_repo
        self.dispatcher=dispatcher

    async def execute(self, message_id: UUID):
        message = await self.email_message_repo.find_by_id(message_id)
        if not message:
            raise Exception('')

        await self.dispatcher.dispatch(message)
