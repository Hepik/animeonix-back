from sqlalchemy import Column, Integer, Enum, ForeignKey, MetaData
from sqlalchemy.orm import relationship
import enum

from config.database import Base

metadata = MetaData()

class ReactionTypeEnum(enum.Enum):
    like = "like"
    dislike = "dislike"

class Reaction(Base):
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title_id = Column(Integer, ForeignKey("titles.id", ondelete="CASCADE"), nullable=True)
    review_id = Column(Integer, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=True)
    type = Column(Enum(ReactionTypeEnum), nullable=False)

    user = relationship("Users", back_populates="reaction")
    title = relationship("Title", back_populates="reaction")
    review = relationship("Review", back_populates="reaction")
