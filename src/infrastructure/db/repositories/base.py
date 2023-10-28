from typing import Generic, TypeVar

from beanie import Document, PydanticObjectId
from motor.motor_asyncio import AsyncIOMotorClient

Model = TypeVar("Model", bound=Document)


class BaseRepository(Generic[Model]):
    """Base repository MongoDB"""

    def __init__(self, model: type[Model], session: AsyncIOMotorClient) -> None:
        self._model = model
        self._session = session

    async def get_by_id(self, id_: PydanticObjectId) -> Model:
        res_obj = await self._model.get(id_)
        assert res_obj
        return res_obj

    async def get_all(self) -> list[Model]:
        result = await self._model.all().to_list()
        return result

    async def update_obj(self, id_: PydanticObjectId, **kwargs) -> None:
        update_query = {
            "$set": {field: value for field, value in kwargs.items()}
        }
        obj = await self._model.get(id_)
        assert obj
        await obj.update(update_query)

    async def delete_obj(self, id_: PydanticObjectId) -> None:
        obj = await self._model.get(id_)
        assert obj
        await obj.delete()
