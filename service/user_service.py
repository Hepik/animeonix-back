from fastapi import HTTPException, Depends
from typing import Annotated
from schemas.user_schema import *
from repository.user_repository import UserRepository
from dotenv import load_dotenv
import os
import bcrypt
import jwt
from datetime import timedelta, datetime, timezone
from starlette import status

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = 'HS256'

class UserService:
    def __init__(self, repository: Annotated[UserRepository, Depends()]):
        self.repository = repository

    def get_users(self):
        users = self.repository.get_users()
        total = self.repository.get_users_count()
        return {
            "users": users,
            "total": total
        }
    
    def get_user_by_username(self, username: str):
        return self.repository.get_user_by_username(username=username)

    def register_user(self, user_schema: RegisterUserRequest):
        user_data = user_schema.model_dump(exclude_unset=True)
        user_data["hashed_password"] = UserService.get_password_hash(user_data["password"])
        user_data["isActive"] = False
        self.repository.create_user(user_data)

    def create_user(self, user_schema: CreateUserRequest):
        user_data = user_schema.model_dump(exclude_unset=True)
        user_data["hashed_password"] = UserService.get_password_hash(user_data["password"])
        self.repository.create_user(user_data)

    def authenticate_user(self, username: str, password: str):
        user = self.repository.get_user_by_username(username)
        if not user:
            return False
        if not bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
            return False
        return user

    def create_access_token(self, user_id: int, role: str, expires_delta: timedelta):
        expires = datetime.now(timezone.utc) + expires_delta
        encode = {
            'id': user_id,
            'role': role.value,
            'exp': expires,
            }
        return jwt.encode(encode, SECRET_KEY, ALGORITHM)

    def get_current_user(self, token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is not valid.")
        id: int = payload.get('id')
        return self.repository.get_user_by_id(id)

    def change_password(self, current_user, current_password: str, new_password: str):
        if not bcrypt.checkpw(current_password.encode('utf-8'), current_user.hashed_password.encode('utf-8')):
            raise HTTPException(status_code=400, detail="Incorrect current password")

        current_user.hashed_password = UserService.get_password_hash(new_password)

        self.repository.update_user(current_user)

    
    def partial_update_user(self, id: int, user: UserUpdate):
        user_data = user.model_dump(exclude_unset=True)

        if "password" in user_data:
            user_data["hashed_password"] = UserService.get_password_hash(user.password)
            del user_data["password"]
        
        db_user = self.repository.partial_update_user(id=id, user_data=user_data)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user

    def delete_user(self, id: int):
        user_deleted = self.repository.delete_by_id(id=id)
        if not user_deleted:
            raise HTTPException(status_code=404, detail="User not found")
        return {"detail": "User deleted successfully"}

    @staticmethod
    def get_password_hash(password: str) -> str:
        bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(bytes, salt).decode()
    
    class UserServiceException(Exception):
        pass
