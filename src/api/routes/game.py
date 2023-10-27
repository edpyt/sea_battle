from fastapi import APIRouter

from src.infrastructure.db.models import Game

router = APIRouter()


@router.get('/')
async def get_games() -> list[dict]:
    return await Game.all().to_list()
