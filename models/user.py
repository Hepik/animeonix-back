from sqlalchemy import Column, Integer, String, MetaData, Enum
import enum

from config.database import Base

metadata = MetaData()

class RoleEnum(enum.Enum):
    user = "user"
    admin = "admin"

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.user)
