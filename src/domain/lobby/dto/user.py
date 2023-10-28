from pydantic import BaseModel


class UserDTO(BaseModel):
    username: str
    password: str

    class Collection:
        name = 'user'
