from fastapi import APIRouter, FastAPI

from app.api.dependencies.auth.auth_dependencies import CurrentUserDependency
from app.api.dependencies.email_account.oauth_dependencies import ConnectEmailAccountUseCaseDependency, DisconnectEmailAccountUseCaseDependency, OAuthCallbackUseCaseDependency


class EmailAccountApiRouteHandler:
    def __init__(self) -> None:
        self.router = APIRouter(prefix='/email-accounts', tags=['Email'])
        self._register_connection_router()
        self._register_oauth_callback__router()
        self._register_disconnect_account_router()

    def register_router(self, app: FastAPI) -> None:
        app.include_router(self.router)

    def _register_connection_router(self) -> None:
        @self.router.get('/connect')
        async def connect_email(current_user: CurrentUserDependency, use_case: ConnectEmailAccountUseCaseDependency):
            url = await use_case.execute(current_user.id)

            return url

    def _register_oauth_callback__router(self) -> None:
        @self.router.get('/callback')
        async def callback_email(code: str, state: str, use_case: OAuthCallbackUseCaseDependency):
            await use_case.execute(code=code, state=state)
            return {
                'message': 'Conta Gmail connectada com sucesso.'
            }

    def _register_disconnect_account_router(self) -> None:
        @self.router.delete('/me')
        async def disconnect_account(current_user: CurrentUserDependency, use_case: DisconnectEmailAccountUseCaseDependency):
            await use_case.execute(current_user.id)
            return {'message': 'Conta Gmail desconectada com sucesso.'}
