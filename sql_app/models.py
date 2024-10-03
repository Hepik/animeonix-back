from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, MetaData
from sqlalchemy.orm import relationship

from .database import Base

metadata = MetaData()

class Title(Base):
    __tablename__ = "titles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    trailer = Column(String, unique=True)
    likes = Column(Integer)
    dislikes = Column(Integer)
    reviews = Column(Integer, default=0)
    image = Column(String)
    slug = Column(String)

    review_list = relationship("Review", back_populates="title", cascade="all, delete-orphan")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    content = Column(String)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    title_id = Column(Integer, ForeignKey("titles.id"))

    title = relationship("Title", back_populates="review_list")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")
