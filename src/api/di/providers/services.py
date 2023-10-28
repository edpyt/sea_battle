from fastapi import Depends

from src.domain.lobby.usecases import GameServices
from src.infrastructure.db.uow import UnitOfWork
from src.api.di.providers.db import uow_provider


def get_game_services(uow: UnitOfWork = Depends(uow_provider)) -> GameServices:
    return GameServices(uow)
