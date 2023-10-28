from typing import Generator

from fastapi_users.db import BeanieUserDatabase

from src.infrastructure.db.models import User


async def get_user_db() -> Generator[BeanieUserDatabase, None, None]:
    yield BeanieUserDatabase(User)
