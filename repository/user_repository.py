import models.user
import schemas.user_schema
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from config.database import get_db


class UserRepository:
    def __init__(self, session: Annotated[Session, Depends(get_db)]):
        self.db = session

    def get_users(self):
        return self.db.query(models.user.Users).all()
    

    def get_users_count(self):
        return self.db.query(models.user.Users).count()

    def create_user(self, user_data: dict):
        create_user_model = models.user.Users(
            username=user_data.get("username"),
            email=user_data.get("email"),
            hashed_password = user_data.get("hashed_password"),
            role=user_data.get("role"),
        )

        self.db.add(create_user_model)
        self.db.commit()

    def get_by_username(self, username: str):
        user = self.db.query(models.user.Users).filter(models.user.Users.username == username).first()
        return user

    def partial_update_user(self, id: int, user_data: schemas.user_schema.UserUpdate):
        db_user = self.db.query(models.user.Users).filter(models.user.Users.id == id).first()
        if not db_user:
            return None

        for field, value in user_data.dict(exclude_unset=True).items():
            setattr(db_user, field, value)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user

    def delete_by_id(self, id: int):
        db_user = self.db.query(models.user.Users).filter(models.user.Users.id == id).first()
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False
