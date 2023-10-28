from fastapi import Depends

from src.api.di.db import uow_provider
from src.domain.lobby.usecases import GameServices
from src.infrastructure.db.uow import UnitOfWork


def get_game_services(uow: UnitOfWork = Depends(uow_provider)) -> GameServices:
    return GameServices(uow)
