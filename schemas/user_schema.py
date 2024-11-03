from pydantic import BaseModel
from typing import List, Optional
from models.user import RoleEnum

class UsersBase(BaseModel):
    username: str
    hashed_password: str
    role: RoleEnum

class Users(UsersBase):
    id: int

    class Config:
        from_attributes = True

class Response(BaseModel):
    id: int
    username: str
    role: RoleEnum

class UsersResponse(BaseModel):
    users: List[Response]

    class Config:
        from_attributes = True

class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: RoleEnum

class UserUpdate(BaseModel):
    username: Optional[str] = None
    hashed_password: Optional[str] = None
    role: Optional[RoleEnum] = None

    class Config:
        from_attributes = True

class DeleteResponse(BaseModel):
    detail: str
