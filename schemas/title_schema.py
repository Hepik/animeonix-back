from typing import List, Optional

from pydantic import BaseModel

class TitleBase(BaseModel):
    name: str
    description: str
    trailer: str
    likes: int
    dislikes: int
    reviews: int
    image: str
    slug: str

class TitleCreate(TitleBase):
    pass

class Title(TitleBase):
    id: int

    class Config:
        orm_mode = True

class TitleResponse(BaseModel):
    titles: List[Title]
    total: int
    page: int
    limit: int

    class Config:
        orm_mode = True

class TitleUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    trailer: Optional[str]
    likes: Optional[int]
    dislikes: Optional[int]
    reviews: Optional[int]
    image: Optional[str]
    slug: Optional[str]

    class Config:
        orm_mode = True

class DeleteResponse(BaseModel):
    detail: str
