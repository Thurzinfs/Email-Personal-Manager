from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.exceptions_handlers.domain_handlers import (
    domain_exception_handler,
)
from app.api.handlers.user.user_api_route_handler import UserAPiRouteHandler
from app.infrastructure.database.sqlite.database import close_db, init_models

from app.infrastructure.database.sqlite.database import alchemy
from config.exception import BaseDomainException


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_models()
    yield
    await close_db()


app = FastAPI(
    title='Email Personal Manager',
    description='Uma api RESTfull desenvolvida com python utilizando o advanced alchemy como orm afim de estudo.',
    version='0.0.1',
    lifespan=lifespan,
    root_path='/api/v1',
)
alchemy.init_app(app)

app.add_exception_handler(BaseDomainException, domain_exception_handler)  # type: ignore


@app.get('/health', tags=['Health'])
def health_check():
    return {'message': 'OK'}


user_route_handler = UserAPiRouteHandler()
user_route_handler.register_router(app)
