from beanie import Document


class User(Document):
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "UserName",
                "password": "b7119a51aadb98012c5ab59a88120f64e8bc8bfc97ee"
            }
        }
    
    class Settings:
        name = "user"
