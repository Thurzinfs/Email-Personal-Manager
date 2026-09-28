from datetime import datetime, timedelta, timezone
import hashlib
from typing import Tuple
from uuid import UUID, uuid4

import jwt

from app.domain.contracts.auth.servicies import IRefreshTokenServices
from app.domain.entities.auth.refresh_token_entity import RefreshTokenEntity
from app.domain.exceptions.auth_exceptions import TokenExpiredException
from config.settings import settings


class AuthTokenService(IRefreshTokenServices):
    def hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def decode_token(self, hash: str) -> dict:
        try:
            return jwt.decode(
                hash, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )

        except jwt.ExpiredSignatureError:
            raise TokenExpiredException()

    def create_access_token(self, user: UUID) -> str:
        payload = {
            'sub': str(user),
            'type': 'access',
            'exp': datetime.now(timezone.utc)
            + timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)),
        }

        return jwt.encode(payload, settings.SECRET_KEY, settings.ALGORITHM)

    def create_refresh_token(
        self, user: UUID
    ) -> Tuple[str, RefreshTokenEntity]:
        raw_token = str(uuid4())

        hash_token = self.hash_token(raw_token)

        refresh = RefreshTokenEntity(
            user=user,
            token_hash=hash_token,
            expire_at=datetime.now(timezone.utc)
            + timedelta(days=int(settings.REFRESH_TOKEN_EXPIRE_DAYS)),
        )

        return hash_token, refresh
