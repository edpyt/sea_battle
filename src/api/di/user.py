from typing import AsyncGenerator

from fastapi_users.db import BeanieUserDatabase

from src.infrastructure.db.models import User


async def get_user_db() -> AsyncGenerator[BeanieUserDatabase, None]:
    yield BeanieUserDatabase(User)
