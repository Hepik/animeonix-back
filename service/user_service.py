from fastapi import HTTPException, Depends
from typing import Annotated
from schemas.user_schema import *
from repository.user_repository import UserRepository
from dotenv import load_dotenv
import os
import bcrypt
import jwt
from datetime import timedelta, datetime, timezone
from fastapi.security import OAuth2PasswordBearer
from starlette import status

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = 'HS256'


oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

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

    def create_user(self, user_data: CreateUserRequest):
        bytes = user_data.password.encode('utf-8')
        salt = bcrypt.gensalt() 
        hash = bcrypt.hashpw(bytes, salt)
        user_data.password = hash
        self.repository.create_user(user_data)

    def authenticate_user(self, username: str, password: str):
        user = self.repository.get_by_username(username)
        if not user:
            return False
        if not bcrypt.checkpw(password.encode('utf-8'), user.hashed_password):
            return False
        return user

    def create_access_token(self, username: str, user_id: int, expires_delta: timedelta):
        expires = datetime.now(timezone.utc) + expires_delta
        encode = {'sub': username, 'id': user_id, 'exp': expires}
        return jwt.encode(encode, SECRET_KEY, ALGORITHM)

    def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get('sub')
            user_id: int = payload.get('id')
            if username is None or user_id is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
            return {'username': username, 'id': user_id}
        except:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

    def partial_update_user(self, id: int, user: UserUpdate):
        db_title = self.repository.partial_update_user(id=id, user_data=user)
        if db_title is None:
            raise HTTPException(status_code=404, detail="User not found")
        return db_title

    def delete_user(self, id: int):
        user_deleted = self.repository.delete_by_id(id=id)
        if not user_deleted:
            raise HTTPException(status_code=404, detail="User not found")
        return {"detail": "User deleted successfully"}
