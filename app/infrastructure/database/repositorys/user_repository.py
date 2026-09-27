from uuid import UUID

from typing import List

from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from app.domain.entities.user.user_entities import UserEntity
from app.domain.contracts.user.repositories import IUserRepository
from app.infrastructure.models.user_models import User


class AdvancedUserRepository(SQLAlchemyAsyncRepository[User], IUserRepository):
    model_type = User

    async def save(self, user: UserEntity) -> UserEntity:
        model = self._entity_to_model(user)

        saved_model = await self.upsert(model, auto_commit=True)
        return self._model_to_entity(saved_model)

    async def find_by_id(self, id: UUID) -> UserEntity | None:
        model = await self.get_one_or_none(id=id)
        if not model:
            return None

        return self._model_to_entity(model)

    async def find_by_email(self, email: str) -> UserEntity | None:
        model = await self.get_one_or_none(email=email)
        if not model:
            return None

        return self._model_to_entity(model)

    async def list_users(self) -> List[UserEntity]:
        models = await self.list()
        return [self._model_to_entity(model) for model in models]

    async def verify_exists_email(self, email: str) -> bool:
        return await self.exists(email=email)

    def _entity_to_model(self, entity: UserEntity) -> User:
        return User(
            id=entity.id,
            name=entity.name,
            email=entity.email,
            password=entity.password,
            created_at=entity.created_at,
        )

    def _model_to_entity(self, model: User) -> UserEntity:
        return UserEntity(
            id=model.id,
            name=model.name,
            email=model.email,
            password=model.password,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
