from beanie import PydanticObjectId
from fastapi_users import FastAPIUsers

from src.api.di.user import get_auth_backend, get_user_manager
from src.infrastructure.db.models import User

fastapi_users = (
    FastAPIUsers[User, PydanticObjectId]
    (get_user_manager, [get_auth_backend()])
)

current_active_user = fastapi_users.current_user(active=True)
