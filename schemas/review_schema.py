from typing import List

from pydantic import BaseModel

class ReviewBase(BaseModel):
    content: str
    likes: int
    dislikes: int
    title_id: int

class ReviewCreate(BaseModel):
    content: str
    title_id: int

class Review(ReviewBase):
    id: int

    class Config:
        orm_mode = True

class ReviewResponse(BaseModel):
    reviews: List[Review]
    total: int
    page: int
    limit: int

    class Config:
        orm_mode = True

class DeleteResponse(BaseModel):
    detail: str
