from fastapi import APIRouter, Depends

from src.domain.user.interfaces import current_active_user
from src.infrastructure.db.models.user import User

router = APIRouter()


@router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}
