from motor.motor_asyncio import AsyncIOMotorClient

from src.infrastructure.db.repositories import GameRepository, UserRepository


class LobbyHolder:
    def __init__(self, session: AsyncIOMotorClient) -> None:
        self.user_repo = UserRepository(session)
        self.game_repo = GameRepository(session)


class UnitOfWork:
    def __init__(self, session: AsyncIOMotorClient) -> None:
        self.lobby_holder = LobbyHolder(session)
