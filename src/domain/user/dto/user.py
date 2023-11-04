from typing import Optional

from pydantic import BaseModel


class UserDTO(BaseModel):
    username: str
    email: Optional[str]
    password: str
