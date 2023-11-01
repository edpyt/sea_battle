from typing import Optional

from beanie import PydanticObjectId
from fastapi_users import schemas
from pydantic import EmailStr


class UserRead(schemas.BaseUser[PydanticObjectId]):
    username: str
    email: Optional[EmailStr]


class UserCreate(schemas.BaseUserCreate):
    username: str
    email: Optional[EmailStr] = None


class UserUpdate(schemas.BaseUserUpdate):
    username: str
    email: Optional[EmailStr]
