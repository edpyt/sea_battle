import logging
from typing import AsyncGenerator

from fastapi import Depends, WebSocket, WebSocketException
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import BeanieUserDatabase

from src.core.config import settings
from src.domain.user.interfaces.manager import UserManager
from src.infrastructure.db.models import User

logger = logging.getLogger("uvicorn")


async def get_user_db() -> AsyncGenerator[BeanieUserDatabase, None]:
    yield BeanieUserDatabase(User)


async def get_user_manager(
    user_db: BeanieUserDatabase = Depends(get_user_db)
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET, lifetime_seconds=3600)


def get_auth_backend() -> AuthenticationBackend:
    bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
    auth_backend = AuthenticationBackend(
        name='jwt', transport=bearer_transport, get_strategy=get_jwt_strategy
    )
    return auth_backend


async def get_user_from_token(
    websocket: WebSocket,
    auth_backend: AuthenticationBackend = Depends(get_auth_backend),
    user_manager: UserManager = Depends(get_user_manager)
) -> AsyncGenerator[User, None]:
    token = websocket.headers.get("fastapiusersauth")
    user = await auth_backend.get_strategy().read_token(token, user_manager)
    print(token)
    if not user or not user.is_active:
        logger.error('User is not provided or is not active')
        raise WebSocketException("Invalid user")
    yield user
