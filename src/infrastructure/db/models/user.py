from typing import Optional

from beanie import Document, Indexed
from fastapi_users.db import BeanieBaseUser


class User(BeanieBaseUser, Document):
    username: Indexed(str, unique=True)  # type: ignore
    email: Optional[Indexed(str, unique=False)] = None  # type: ignore
