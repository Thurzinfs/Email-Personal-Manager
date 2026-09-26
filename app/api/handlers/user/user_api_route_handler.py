from uuid import UUID

from fastapi import APIRouter, FastAPI

from starlette import status

from app.api.dependencies import RegisterUserUseCaseDependencie, ResponseUserUseCaseDependencie
from app.api.schemas import UserInSchema, UserOutSchema


class UserAPiRouteHandler:
    def __init__(self) -> None:
        self.router = APIRouter(prefix='/users', tags=['User'])
        self._register_post_router()
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
            data: UserInSchema, use_case: RegisterUserUseCaseDependencie
        ):
            dto = data.to_dto()

            user = await use_case.execute(dto)

            return UserOutSchema.from_domain(user)

    def _register_get_router(self) -> None:
        @self.router.get(
            '/{id}',
            response_model=UserOutSchema,
            status_code=status.HTTP_200_OK
        )
        async def response_user(id: UUID, use_case: ResponseUserUseCaseDependencie):
            user = await use_case.execute(id)

            return UserOutSchema.from_domain(user)
