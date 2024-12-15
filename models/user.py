from sqlalchemy import Column, Integer, String, MetaData, Enum, Boolean
import enum
from sqlalchemy.orm import relationship

from config.database import Base

metadata = MetaData()

class RoleEnum(enum.Enum):
    user = "user"
    admin = "admin"

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.user)
    isActive = Column(Boolean, nullable=False, default=False)
    avatar = Column(String, default="/static/default_user_avatar.jpg")

    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    reaction = relationship("Reaction", back_populates="user", cascade="all, delete-orphan")
