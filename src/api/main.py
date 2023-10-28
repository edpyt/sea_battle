from fastapi import FastAPI

from src.api.routes import game_router, user_router
from src.domain.user.interfaces import auth_backend, fastapi_users
from src.domain.user.schemas import UserCreate, UserRead, UserUpdate
from src.infrastructure.db.main import initiate_database

app = FastAPI()


@app.on_event("startup")
async def start_database() -> None:
    await initiate_database()


app.include_router(game_router, prefix='/games')
app.include_router(user_router)

# FastAPI Users
app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
