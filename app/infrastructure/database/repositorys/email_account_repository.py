from uuid import UUID

from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from app.domain.contracts.email_account.repositories import IEmailAccountRepository, IOAuthConnectionRepository
from app.domain.entities.email_account.emai_account_entity import EmailAccountEntity, OAuthConnectionEntity
from app.infrastructure.models.email_account_model import EmailAccount, OAuthConnection


class AdvancedEmailAccountRepository(SQLAlchemyAsyncRepository[EmailAccount], IEmailAccountRepository):
    model_type = EmailAccount

    async def save(self, entity: EmailAccountEntity) -> EmailAccountEntity:
        model = self._entity_to_model(entity)

        saved = await self.upsert(model, auto_commit=True)
        return self._model_to_entity(saved)

    async def find_by_user_id(self, id: UUID) -> EmailAccountEntity | None:
        model = await self.get_one_or_none(user_id=id)
        if not model:
            return None

        return self._model_to_entity(model)

    def _model_to_entity(self, model: EmailAccount) -> EmailAccountEntity:
        return EmailAccountEntity(
            id=model.id,
            user=model.user.id,
            provider=model.provider,
            email_address=model.email_address,
            access_token=model.access_token,
            refresh_token=model.refresh_token,
            token_expire_at=model.token_expire_at,
            scopes=model.scopes.split(',') if model.scopes else [],
            connected=model.connected,
            connected_at=model.connected_at
        )

    def _entity_to_model(self, entity: EmailAccountEntity) -> EmailAccount:
        return EmailAccount(
            id=entity.id,
            user_id=entity.user,
            provider=entity.provider,
            email_address=entity.email_address,
            access_token=entity.access_token,
            refresh_token=entity.refresh_token,
            token_expire_at=entity.token_expire_at,
            scopes=','.join(entity.scopes),
            connected=entity.connected,
            connected_at=entity.connected_at
        )


class AdvancedOAuthConnectionRepository(SQLAlchemyAsyncRepository[OAuthConnection], IOAuthConnectionRepository):
    model_type = OAuthConnection

    async def save(self, entity: OAuthConnectionEntity) -> OAuthConnectionEntity:
        model = self._entity_to_model(entity)

        saved = await self.upsert(model, auto_commit=True)
        return self._model_to_entity(saved)

    async def find_by_state(self, state: str) -> OAuthConnectionEntity | None:
        model = await self.get_one_or_none(state=state)
        if not model:
            return None

        return self._model_to_entity(model)

    async def delete_by_state(self, state: str) -> None:
        await self.delete(state, id_attribute='state')

    def _model_to_entity(self, model: OAuthConnection) -> OAuthConnectionEntity:
        return OAuthConnectionEntity(
            state=model.state,
            user_id=model.user_id,
            code_verifier=model.code_verifier,
            created_at=model.created_at,
            expire_at=model.expire_at
        )

    def _entity_to_model(self, entity: OAuthConnectionEntity) -> OAuthConnection:
        return OAuthConnection(
            state=entity.state,
            user_id=entity.user_id,
            code_verifier=entity.code_verifier,
            created_at=entity.created_at,
            expire_at=entity.expire_at
        )
