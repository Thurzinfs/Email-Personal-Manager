from enum import Enum
from typing import List
from uuid import UUID

from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from app.domain.contracts.email_message.repositories import IEmailMessageRepository
from app.domain.entities.email_message.email_message_entity import EmailMessageEntity
from app.domain.entities.email_message.status_message import StatusEmailMessage
from app.domain.value_objects.scheduled_at_vo import ScheduledAtVO
from app.infrastructure.models.email_message_model import EmailMessage


class AdvancedEmailMessageRepository(SQLAlchemyAsyncRepository[EmailMessage], IEmailMessageRepository):
    model_type = EmailMessage

    async def save(self, entity: EmailMessageEntity) -> EmailMessageEntity:
        model = self._entity_to_model(entity)

        saved = await self.upsert(model, auto_commit=True)

        await self.session.refresh(saved)

        return self._model_to_entity(saved)

    async def find_by_email_account(self, email_account: UUID) -> EmailMessageEntity | None:
        model = await self.get_one_or_none(email_account_id=email_account)
        if not model:
            return None

        return self._model_to_entity(model)

    async def find_by_id(self, id: UUID) -> EmailMessageEntity | None:
        model = await self.get_one_or_none(id=id)
        if not model:
            return None

        return self._model_to_entity(model)

    async def list_messages_by_email_account(self, email_account: UUID) -> List[EmailMessageEntity]:
        return [
            self._model_to_entity(message)
            for message in await self.list(email_account_id=email_account)
        ]

    def _entity_to_model(self, entity: EmailMessageEntity) -> EmailMessage:
        return EmailMessage(
            id=entity.id,
            to_address=entity.to_address,
            subject=entity.subject,
            body=entity.body,
            email_account_id=entity.email_account,
            scheduled_at=entity.scheduled_at.value if entity.scheduled_at else None,
            status=entity.status.value if isinstance(entity.status, Enum) else str(entity.status),
            sent_as=entity.sent_as,
            created_at=entity.created_at
        )

    def _model_to_entity(self, model: EmailMessage) -> EmailMessageEntity:
        return EmailMessageEntity(
            id=model.id,
            to_address=model.to_address,
            subject=model.subject,
            body=model.body,
            email_account=model.email_account_id,
            scheduled_at=ScheduledAtVO(value=model.scheduled_at) if model.scheduled_at else None,
            status=StatusEmailMessage(model.status if isinstance(model.status, Enum) else StatusEmailMessage.PENDING.value),
            sent_as=model.sent_as,
            created_at=model.created_at
        )
    