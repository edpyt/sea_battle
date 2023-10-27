from typing import Any

from fastapi import FastAPI

from src.api.routes import game_router
from src.infrastructure.db.main import initiate_database

app = FastAPI()


@app.on_event("startup")
async def start_database() -> None:
    await initiate_database()


@app.get('/')
async def test_connnection() -> Any:
    return {"message": "Welcome to this fantastic app."}


app.include_router(game_router, prefix='/games')