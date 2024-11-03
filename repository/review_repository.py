import models.review
import schemas.review_schema
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi import Depends
from config.database import get_db


class ReviewRepository:
    def __init__(self, session: Annotated[Session, Depends(get_db)]):
        self.db = session
    
    def get_reviews(self, skip: int = 0, limit: int = 10):
        return self.db.query(models.review.Review).offset(skip).limit(limit).all()

    def get_reviews_count(self):
        return self.db.query(models.review.Review).count()
    
    def get_reviews_by_title(self, title_id: int, skip: int = 0, limit: int = 10):
        return self.db.query(models.review.Review).filter(models.review.Review.title_id == title_id).offset(skip).limit(limit).all()

    def get_reviews_by_title_count(self, title_id: int):
        return self.db.query(models.review.Review).filter(models.review.Review.title_id == title_id).count()

    def get_review_by_id(self, id: int):
        return self.db.query(models.review.Review).filter(models.review.Review.id == id).first()

    def create_review(self, review: schemas.review_schema.ReviewCreate):
        db_review = models.review.Review(
            content=review.content, 
            likes=0, 
            dislikes=0, 
            title_id=review.title_id
        )
        self.db.add(db_review)
        self.db.commit()
        self.db.refresh(db_review)
        return db_review

    def delete_review(self, id: int):
        db_review = self.db.query(models.review.Review).filter(models.review.Review.id == id).first()
        if db_review:
            self.db.delete(db_review)
            self.db.commit()
            return True
        return False
