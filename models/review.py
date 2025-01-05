from sqlalchemy import Column, ForeignKey, Integer, String, MetaData
from sqlalchemy.orm import relationship

from config.database import Base

metadata = MetaData()

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    content = Column(String)
    title_id = Column(Integer, ForeignKey("titles.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    title = relationship("Title", back_populates="review_list")
    user = relationship("Users", back_populates="reviews")
    reaction = relationship("Reaction", back_populates="review", cascade="all, delete-orphan")
