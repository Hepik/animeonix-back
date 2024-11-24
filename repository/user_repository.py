import models.user
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
    
    def get_user_by_username(self, username: str):
        user = self.db.query(models.user.Users).filter(models.user.Users.username == username).first()
        user.avatar = f"http://localhost:8000/images/{user.avatar.split('/')[-1]}"
        return user
    
    def get_user_by_id(self, id: int):
        user = self.db.query(models.user.Users).filter(models.user.Users.id == id).first()
        user.avatar = f"http://localhost:8000/images/{user.avatar.split('/')[-1]}"
        return user

    def create_user(self, user_data: dict):
        create_user_model = models.user.Users(
            username=user_data.get("username"),
            email=user_data.get("email"),
            hashed_password = user_data.get("hashed_password"),
            role=user_data.get("role"),
        )

        self.db.add(create_user_model)
        self.db.commit()

    def update_user(self, db_user: models.user.Users):
        self.db.commit()
        self.db.refresh(db_user)
        return True

    def partial_update_user(self, id: int, user_data: dict):
        db_user = self.db.query(models.user.Users).filter(models.user.Users.id == id).first()
        if not db_user:
            return None

        for field, value in user_data.items():
            if field == "avatar" and isinstance(value, str):
                setattr(db_user, field, value.split('/')[-1])
            else:
                setattr(db_user, field, value)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def user_change_password(self, id: int, current_password: str, new_password: str):
        db_user = self.db.query(models.user.Users).filter(models.user.Users.id == id).first()

        if not bcrypt.checkpw(current_password.encode('utf-8'), db_user.hashed_password.encode('utf-8')):
            return False

        db_user.hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

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
