from fastapi import Depends, Query, APIRouter
from schemas.review_schema import *
from service.review_service import ReviewService
from typing import Annotated
from utils.auth_utils import oauth2_bearer_user

router = APIRouter(
    prefix="/reviews"
)


@router.get("", response_model=ReviewResponse)
def get_reviews(service: Annotated[ReviewService, Depends()],
                         title_id: int = Query(None),
                         page: int = Query(1),
                         limit: int = Query(10)):
    return service.get_reviews(page=page, limit=limit, title_id=title_id)


@router.get("/{id}", response_model=Review)
def get_review_by_id(id: int, service: Annotated[ReviewService, Depends()]):
    return service.get_review_by_id(id=id)


@router.post("", response_model=Review)
def create_review(
    current_user: Annotated[str, Depends(oauth2_bearer_user)], 
    review: ReviewCreate, 
    service: Annotated[ReviewService, Depends()]
):
    return service.create_review(review=review, user_id=current_user.id)


@router.delete("/{id}", response_model=DeleteResponse)
def delete_review(_: Annotated[str, Depends(oauth2_bearer_user)], id: int, service: Annotated[ReviewService, Depends()]):
    service.delete_review(id=id)
    return {"detail": "Review deleted successfully"}
