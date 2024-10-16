from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session
from schemas.review_schema import *
from repository.review_repository import ReviewRepository


class ReviewService:
    def __init__(self, session: Session):
        self.repository = ReviewRepository(session)
    
    def get_reviews(self, page: int, limit: int):
        skip = (page - 1) * limit
        reviews = self.repository.get_reviews(skip=skip, limit=limit)
        total = self.repository.get_reviews_count()
        return {
            "reviews": reviews,
            "total": total,
            "page": page,
            "limit": limit
        }


    def get_reviews_by_title(self, title_id: int,  page: int, limit: int):
        skip = (page - 1) * limit
        reviews = self.repository.get_reviews_by_title(skip=skip, limit=limit, title_id=title_id)
        total = self.repository.get_reviews_by_title_count(title_id=title_id)
        return {
            "reviews": reviews,
            "total": total,
            "page": page,
            "limit": limit
        }


    def get_review_by_id(self, id: int):
        review = self.repository.get_review_by_id(id=id)
        return review


    def create_review(
        self, 
        title_id: int, 
        review: ReviewCreate
    ):
        return self.repository.create_review(review=review, title_id=title_id)


    def delete_review(self, review_id: int):
        review_deleted = self.repository.delete_review(review_id=review_id)
        if not review_deleted:
            raise HTTPException(status_code=404, detail="Review not found")
        return {"detail": "Review deleted successfully"}