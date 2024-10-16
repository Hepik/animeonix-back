from sqlalchemy import Column, ForeignKey, Integer, String, MetaData
from sqlalchemy.orm import relationship

from config.database import Base

metadata = MetaData()

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    content = Column(String)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    title_id = Column(Integer, ForeignKey("titles.id"))

    title = relationship("Title", back_populates="review_list")
