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

class TitleCreate(BaseModel):
    name: str
    description: str
    trailer: str
    image: str
    slug: str

class Title(TitleBase):
    id: int

    class Config:
        from_attributes = True

class TitleResponse(BaseModel):
    titles: List[Title]
    total: int
    page: int
    limit: int

    class Config:
        from_attributes = True

class TitleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    trailer: Optional[str] = None
    likes: Optional[int] = None
    dislikes: Optional[int] = None
    reviews: Optional[int] = None
    image: Optional[str] = None
    slug: Optional[str] = None

    class Config:
        from_attributes = True

class DeleteResponse(BaseModel):
    detail: str
