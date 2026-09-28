from typing import List
from uuid import UUID

from fastapi import APIRouter, FastAPI

from starlette import status

from app.api.dependencies.user.user_dependencies import (
    ListUsersUseCaseDependency,
    RegisterUserUseCaseDependency,
    ResponseUserUseCaseDependency,
)
from app.api.schemas.user.user_schemas import UserInSchema, UserOutSchema


class UserAPiRouteHandler:
    def __init__(self) -> None:
        self.router = APIRouter(prefix='/users', tags=['User'])
        self._register_post_router()
        self._register_get_list_router()
        self._register_get_router()

    def register_router(self, app: FastAPI) -> None:
        app.include_router(self.router)

    def _register_post_router(self) -> None:
        @self.router.post(
            '/',
            response_model=UserOutSchema,
            status_code=status.HTTP_201_CREATED,
        )
        async def register_user(
            data: UserInSchema, use_case: RegisterUserUseCaseDependency
        ):
            dto = data.to_dto()

            user = await use_case.execute(dto)

            return UserOutSchema.from_domain(user)

    def _register_get_router(self) -> None:
        @self.router.get(
            '/{id}',
            response_model=UserOutSchema,
            status_code=status.HTTP_200_OK,
        )
        async def response_user(
            id: UUID, use_case: ResponseUserUseCaseDependency
        ):
            user = await use_case.execute(id)

            return UserOutSchema.from_domain(user)

    def _register_get_list_router(self) -> None:
        @self.router.get(
            '/list',
            response_model=List[UserOutSchema],
            status_code=status.HTTP_200_OK,
        )
        async def list_users(use_case: ListUsersUseCaseDependency):
            users = await use_case.execute()

            return [UserOutSchema.from_domain(user) for user in users]
