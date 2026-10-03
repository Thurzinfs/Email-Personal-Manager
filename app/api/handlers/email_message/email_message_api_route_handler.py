from fastapi import APIRouter, FastAPI

from app.api.dependencies.auth.auth_dependencies import CurrentUserDependency
from app.api.dependencies.email_message.email_message_dependencies import RegisterEmailMessageUseCaseDependency
from app.api.schemas.email_message.email_message_schemas import EmailMessageInSchema, EmailMessageOutSchema


class EmailMessageApiRouterHandler:
    def __init__(self) -> None:
        self.router = APIRouter(prefix='/messages', tags=['Messages'])
        self._register_create_message()

    def register_router(self, app: FastAPI) -> None:
        app.include_router(self.router)

    def _register_create_message(self) -> None:
        @self.router.post('', response_model=EmailMessageOutSchema)
        async def create_message(current_user: CurrentUserDependency, data: EmailMessageInSchema, use_case: RegisterEmailMessageUseCaseDependency):
            dto = data.to_dto()

            message = await use_case.execute(current_user.id, dto)

            return EmailMessageOutSchema.from_domain(message)
        