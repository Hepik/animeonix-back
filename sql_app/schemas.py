from typing import Union, List, Optional

from pydantic import BaseModel

class ReviewModel(BaseModel):
    content: str

class ReviewBase(BaseModel):
    content: str
    likes: int
    dislikes: int
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

class ItemBase(BaseModel):
    title: str
    description: Union[str, None] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []

    class Config:
        orm_mode = True
