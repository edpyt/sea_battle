from typing import Optional

from beanie import Document, Indexed, PydanticObjectId
from fastapi_users.db import BeanieBaseUser


class User(BeanieBaseUser, Document):
    username: Indexed(str, unique=True)  # type: ignore
    email: Optional[Indexed(str, unique=False)] = None  # type: ignore

    @classmethod
    async def get_by_username(cls, username: str) -> Optional["User"]:
        """
        Get a single user by username

        Params:
            username(str): Unique username field
        """
        return await cls.find_one(cls.username == username)

    @classmethod
    async def get_by_id(cls, id_: PydanticObjectId) -> Optional["User"]:
        """
        Get by MongoDB id

        Params:
            id_(PydanticObjectId): MongoDB document ObjectID "_id" field.
        """
        return await cls.find_one(cls.id == id_)
