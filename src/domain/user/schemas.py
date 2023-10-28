from beanie import PydanticObjectId
from fastapi_users import schemas


class UserRead(schemas.BaseUser[PydanticObjectId]):
    ...


class UserCreate(schemas.BaseUserCreate):
    ...


class UserUpdate(schemas.BaseUserUpdate):
    ...
