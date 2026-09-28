from typing import Annotated

from fastapi import APIRouter, Cookie, FastAPI, HTTPException, Response
from starlette import status

from app.api.dependencies.auth.auth_dependencies import (
    CurrentUserDependency,
    LoginUserUseCaseDependency,
    LogoutUserUseCaseDependency,
    RefreshTokenUseCaseDependency,
)
from app.api.schemas.auth.auth_schemas import LoginInSchema, LoginOutSchema
from app.api.schemas.user.user_schemas import UserOutSchema
from config.settings import settings


class AuthApiRouteHandler:
    def __init__(self) -> None:
        self.router = APIRouter(prefix='/auth', tags=['Auth'])
        self._register_login_router()
        self._register_logout_router()
        self._register_refresh_token_router()
        self._register_me_request_router()

    def register_router(self, app: FastAPI) -> None:
        app.include_router(self.router)

    def _register_login_router(self):
        @self.router.post('/login', status_code=status.HTTP_200_OK)
        async def login_user(
            response: Response,
            data: LoginInSchema,
            use_case: LoginUserUseCaseDependency,
        ):
            dto = data.to_dto()

            tokens = await use_case.execute(dto)

            response.set_cookie(
                key='access_token',
                value=f'Bearer {tokens.access_token}',
                httponly=True,
                secure=True,
                samesite='lax',
                max_age=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES) * 60,
                path='/',
            )

            response.set_cookie(
                key='refresh_token',
                value=tokens.refresh_token,
                httponly=True,
                secure=True,
                samesite='lax',
                max_age=int(settings.REFRESH_TOKEN_EXPIRE_DAYS) * 60 * 60,
                path='/',
            )

            return {'message': 'Login realizado com sucesso.'}

    def _register_me_request_router(self) -> None:
        @self.router.get('/me', response_model=UserOutSchema)
        async def request_me(current_user: CurrentUserDependency):
            return current_user

    def _register_logout_router(self) -> None:
        @self.router.post('/logout')
        async def logout_user(
            response: Response,
            current_user: CurrentUserDependency,
            use_case: LogoutUserUseCaseDependency,
        ):
            await use_case.execute(current_user.id)

            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')

    def _register_refresh_token_router(self) -> None:
        @self.router.post(
            '/refresh',
            status_code=status.HTTP_200_OK,
        )
        async def refresh_token(
            response: Response,
            use_case: RefreshTokenUseCaseDependency,
            refresh: Annotated[
                str | None,
                Cookie(alias='refresh_token', include_in_schema=False),
            ] = None,
        ):
            if not refresh:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Cookie de renovação ausente.",
                )
            tokens = await use_case.execute(refresh)

            response.set_cookie(
                key='access_token',
                value=f'Bearer {tokens.access_token}',
                httponly=True,
                secure=True,
                samesite='lax',
                max_age=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES) * 60,
                path='/',
            )

            response.set_cookie(
                key='refresh_token',
                value=tokens.refresh_token,
                httponly=True,
                secure=True,
                samesite='lax',
                max_age=int(settings.REFRESH_TOKEN_EXPIRE_DAYS) * 60 * 60,
                path='/',
            )
