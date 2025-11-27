from pydantic import BaseModel

class UserRead(BaseModel):
    id: int
    email: str
    is_admin: bool

    class Config:
        from_attributes = True
