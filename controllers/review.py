from fastapi import Depends, Query, APIRouter
from schemas.review_schema import *
from service.review_service import ReviewService
from typing import Annotated

router = APIRouter(
    prefix="/reviews"
)

@router.get("", response_model=ReviewResponse)
def get_reviews(service: Annotated[ReviewService, Depends()], page: int = Query(1), limit: int = Query(10)):
    return service.get_reviews(page=page, limit=limit)


@router.get("/{title_id}", response_model=ReviewResponse)
def get_reviews_by_title(service: Annotated[ReviewService, Depends()], title_id: int, page: int = Query(1), limit: int = Query(10)):
    return service.get_reviews_by_title(page=page, limit=limit, title_id=title_id)


@router.get("/review_id/{id}", response_model=Review)
def get_review_by_id(id: int, service: Annotated[ReviewService, Depends()]):
    return service.get_review_by_id(id=id)


@router.post("/{title_id}", response_model=Review)
def create_review(
    title_id: int, 
    review: ReviewCreate, 
    service: Annotated[ReviewService, Depends()]
):
    return service.create_review(title_id=title_id, review=review)


@router.delete("/{review_id}", response_model=DeleteResponse)
def delete_review(review_id: int, service: Annotated[ReviewService, Depends()]):
    service.delete_review(review_id=review_id)
    return {"detail": "Review deleted successfully"}
