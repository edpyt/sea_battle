from fastapi import Depends

from src.api.di.db import uow_provider
from src.api.di.user import get_user_manager
from src.domain.game.usecases.game import GameServices
from src.domain.user.interfaces.manager import UserManager
from src.domain.user.usecases.user import UserServices
from src.infrastructure.db.uow import UnitOfWork


def get_game_services(uow: UnitOfWork = Depends(uow_provider)) -> GameServices:
    return GameServices(uow)


def get_user_services(
    uow: UnitOfWork = Depends(uow_provider),
    user_manager: UserManager = Depends(get_user_manager)
) -> UserServices:
    return UserServices(uow, user_manager)
