from fastapi import HTTPException, Depends
from schemas.review_schema import *
from repository.review_repository import ReviewRepository
from typing import Annotated


class ReviewService:
    def __init__(self, repository: Annotated[ReviewRepository, Depends()]):
        self.repository = repository


    def get_reviews(self, title_id: int,  page: int, limit: int):
        skip = (page - 1) * limit

        if not title_id:
            reviews = self.repository.get_reviews(skip=skip, limit=limit)
            total = self.repository.get_reviews_count()
        else:
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
        review: ReviewCreate
    ):
        return self.repository.create_review(review=review)


    def delete_review(self, id: int):
        review_deleted = self.repository.delete_review(id=id)
        if not review_deleted:
            raise HTTPException(status_code=404, detail="Review not found")
        return {"detail": "Review deleted successfully"}
