from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

load_dotenv()
IMAGE_DIR = os.getenv("IMAGE_DIR")

app = FastAPI()
app.mount("/images", StaticFiles(directory=IMAGE_DIR), name="images")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/titles", response_model=schemas.TitleResponse)
def get_titles(page: int = Query(1), limit: int = Query(10), db: Session = Depends(get_db)):
    skip = (page - 1) * limit
    titles = crud.get_titles(db, skip=skip, limit=limit)
    total = crud.get_title_count(db)
    return {
        "titles": titles,
        "total": total,
        "page": page,
        "limit": limit
    }


# @app.get("/titles/{id}", response_model=schemas.Title)
# def get_title_by_id(id: int, db: Session = Depends(get_db)):
#     title = crud.get_title_by_id(db, id=id)
#     if not title:
#         raise HTTPException(status_code=404, detail="Title not found")
#     return title


@app.get("/titles/{slug}", response_model=schemas.Title)
def get_title_by_slug(slug: str, db: Session = Depends(get_db)):
    title = crud.get_title_by_slug(db, slug=slug)
    if not title:
        raise HTTPException(status_code=404, detail="Title not found")
    return title


@app.post("/title/", response_model=schemas.Title)
def create_title(title: schemas.TitleCreate, db: Session = Depends(get_db)):
    db_title = crud.create_title(db=db, title=title)
    return db_title


@app.put("/titles/{title_id}", response_model=schemas.Title)
def update_title(title_id: int, title: schemas.TitleCreate, db: Session = Depends(get_db)):
    db_title = crud.update_title(db, title_id=title_id, title_data=title)
    if db_title is None:
        raise HTTPException(status_code=404, detail="Title not found")
    return db_title


@app.patch("/titles/{title_id}", response_model=schemas.Title)
def partial_update_title(title_id: int, title: schemas.TitleUpdate, db: Session = Depends(get_db)):
    db_title = crud.partial_update_title(db, title_id=title_id, title_data=title)
    if db_title is None:
        raise HTTPException(status_code=404, detail="Title not found")
    return db_title


@app.delete("/titles/{title_id}", response_model=schemas.DeleteResponse)
def delete_title(title_id: int, db: Session = Depends(get_db)):
    title_deleted = crud.delete_title(db, title_id=title_id)
    if not title_deleted:
        raise HTTPException(status_code=404, detail="Title not found")
    return {"detail": "Title deleted successfully"}


@app.get("/reviews/{title_id}", response_model=schemas.ReviewResponse)
def get_reviews(title_id: int, page: int = Query(1), limit: int = Query(10), db: Session = Depends(get_db)):
    skip = (page - 1) * limit
    reviews = crud.get_reviews(db, title_id=title_id, skip=skip, limit=limit)
    total = crud.get_review_count(db)
    return {
        "reviews": reviews,
        "total": total,
        "page": page,
        "limit": limit
    }


@app.post("/reviews/{title_id}", response_model=schemas.Review)
def create_review_for_title(
    title_id: int, 
    review: schemas.ReviewModel, 
    db: Session = Depends(get_db)
):
    return crud.create_review(db=db, review=review, title_id=title_id)


@app.delete("/reviews/{review_id}", response_model=schemas.DeleteResponse)
def delete_review(review_id: int, db: Session = Depends(get_db)):
    review_deleted = crud.delete_review(db, review_id=review_id)
    if not review_deleted:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"detail": "Review deleted successfully"}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items
