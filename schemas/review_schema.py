from typing import List

from pydantic import BaseModel

class ReviewBase(BaseModel):
    content: str
    likes: int
    dislikes: int
    title_id: int
    user_id: int

class ReviewCreate(BaseModel):
    content: str
    title_id: int

class Review(ReviewBase):
    id: int

    class Config:
        from_attributes = True

class ReviewResponse(BaseModel):
    reviews: List[Review]
    total: int
    page: int
    limit: int

    class Config:
        from_attributes = True

class DeleteResponse(BaseModel):
    detail: str
