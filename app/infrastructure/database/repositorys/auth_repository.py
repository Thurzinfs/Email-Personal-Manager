from typing import List
from uuid import UUID

from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from app.domain.contracts.auth.repositories import IRefreshTokenRepository
from app.domain.entities.auth.refresh_token_entity import RefreshTokenEntity
from app.infrastructure.models.refresh_token_model import RefreshToken


class AdvancedRefreshTokenRepository(
    SQLAlchemyAsyncRepository[RefreshToken], IRefreshTokenRepository
):
    model_type = RefreshToken

    async def save(self, refresh: RefreshTokenEntity) -> RefreshTokenEntity:
        model = self._entity_to_model(refresh)

        saved_model = await self.upsert(model, auto_commit=True)
        return self._model_to_entity(saved_model)

    async def find_by_hash(self, hash: str) -> RefreshTokenEntity | None:
        model = await self.get_one_or_none(token_hash=hash)
        if not model:
            return None

        return self._model_to_entity(model)

    async def list_tokens_by_user(
        self, user: UUID
    ) -> List[RefreshTokenEntity]:
        models = await self.list(user_id=user)
        return [self._model_to_entity(token) for token in models]

    def _entity_to_model(self, entity: RefreshTokenEntity) -> RefreshToken:
        return RefreshToken(
            id=entity.id,
            user_id=entity.user,
            token_hash=entity.token_hash,
            expire_at=entity.expire_at,
            revoked=entity.revoked,
            created_at=entity.created_at,
        )

    def _model_to_entity(self, model: RefreshToken) -> RefreshTokenEntity:
        return RefreshTokenEntity(
            id=model.id,
            user=model.user_id,
            token_hash=model.token_hash,
            revoked=model.revoked,
            expire_at=model.expire_at,
            created_at=model.created_at,
        )
