from fastapi import APIRouter, FastAPI, Response
from starlette import status

from app.api.dependencies.auth.auth_dependencies import LoginUserUseCaseDependencie
from app.api.schemas.auth.auth_schemas import LoginInSchema
from config.settings import settings


class AuthApiRouteHandler:
    def __init__(self) -> None:
        self.router = APIRouter(prefix='/auth', tags=['Auth'])
        self._register_login_router()

    def register_router(self, app: FastAPI) -> None:
        app.include_router(self.router)

    def _register_login_router(self):
        @self.router.post('/login', status_code=status.HTTP_200_OK)
        async def login_user(response: Response, data: LoginInSchema, use_case: LoginUserUseCaseDependencie):
            dto = data.to_dto()

            tokens = await use_case.execute(dto)

            response.set_cookie(
                key='access_token',
                value=f"Bearer {tokens.access_token}",
                httponly=True,
                secure=True,
                samesite='lax',
                max_age=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES) * 60,
                path='/'
            )

            response.set_cookie(
                key='refresh_token',
                value=tokens.refresh_token,
                httponly=True,
                secure=True,
                samesite='lax',
                max_age=int(settings.REFRESH_TOKEN_EXPIRE_DAYS) * 60 * 60,
                path='/'
            )

            return {
                'message': 'Login realizado com sucesso.'
            }
