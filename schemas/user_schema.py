from pydantic import BaseModel
from typing import List, Optional
from models.user import RoleEnum

class UsersBase(BaseModel):
    username: str
    email: str
    hashed_password: str
    role: RoleEnum
    isActive: bool
    avatar: str

class Users(UsersBase):
    id: int

    class Config:
        from_attributes = True

class Response(BaseModel):
    id: int
    username: str
    email: str
    role: RoleEnum
    isActive: bool
    avatar: str

class UsersResponse(BaseModel):
    users: List[Response]
    total: int
    page: int
    limit: int

    class Config:
        from_attributes = True

class RegisterUserRequest(BaseModel):
    username: str
    email: str
    password: str

class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str
    role: RoleEnum

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[RoleEnum] = None
    isActive: Optional[bool] = None
    avatar: Optional[str] = None

    class Config:
        from_attributes = True

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class ResetPasswordRequest(BaseModel):
    new_password: str
    reset_password_token: str

class DeleteResponse(BaseModel):
    detail: str
