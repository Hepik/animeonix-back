from sqlalchemy import Column, Integer, String, MetaData
from sqlalchemy.orm import relationship

from config.database import Base

metadata = MetaData()

class Title(Base):
    __tablename__ = "titles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    trailer = Column(String, unique=True)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    reviews = Column(Integer, default=0)
    image = Column(String)
    slug = Column(String)

    review_list = relationship("Review", back_populates="title", cascade="all, delete-orphan")
