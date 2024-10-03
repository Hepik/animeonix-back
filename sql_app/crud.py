from sqlalchemy.orm import Session

from . import models, schemas

def get_titles(db: Session, skip: int = 0, limit: int = 10):
    titles = db.query(models.Title).offset(skip).limit(limit).all()
    
    for title in titles:
        title.image = f"http://localhost:8000/images/{title.image.split('/')[-1]}"

    return titles

def get_title_by_id(db: Session, id: int):
    title = db.query(models.Title).filter(models.Title.id == id).first()
    title.image = f"http://localhost:8000/images/{title.image.split('/')[-1]}"
    return title

def get_title_by_slug(db: Session, slug: str):
    title = db.query(models.Title).filter(models.Title.slug == slug).first()
    title.image = f"http://localhost:8000/images/{title.image.split('/')[-1]}"
    return title

def get_title_count(db: Session):
    return db.query(models.Title).count()

def create_title(db: Session, title: schemas.TitleCreate):
    db_title = models.Title(
        name=title.name,
        description=title.description,
        trailer=title.trailer,
        likes=title.likes,
        dislikes=title.dislikes,
        reviews=title.reviews,
        image=title.image.split('/')[-1],
        slug=title.slug
    )
    db.add(db_title)
    db.commit()
    db.refresh(db_title)
    return db_title

def update_title(db: Session, title_id: int, title_data: schemas.TitleCreate):
    db_title = db.query(models.Title).filter(models.Title.id == title_id).first()
    if not db_title:
        return None
    
    db_title.name = title_data.name
    db_title.description = title_data.description
    db_title.trailer = title_data.trailer
    db_title.likes = title_data.likes
    db_title.dislikes = title_data.dislikes
    db_title.reviews = title_data.reviews
    db_title.image = title_data.image.split('/')[-1]
    db_title.slug = title_data.slug

    db.commit()
    db.refresh(db_title)
    return db_title


def partial_update_title(db: Session, title_id: int, title_data: schemas.TitleUpdate):
    db_title = db.query(models.Title).filter(models.Title.id == title_id).first()
    if not db_title:
        return None

    for field, value in title_data.dict(exclude_unset=True).items():
        setattr(db_title, field, value)

    db.commit()
    db.refresh(db_title)
    return db_title

def delete_title(db: Session, title_id: int):
    db_title = db.query(models.Title).filter(models.Title.id == title_id).first()
    if db_title:
        db.delete(db_title)
        db.commit()
        return True
    return False

def get_reviews(db: Session, title_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.Review).filter(models.Review.title_id == title_id).offset(skip).limit(limit).all()

def get_review_count(db: Session):
    return db.query(models.Review).count()

def create_review(db: Session, review: schemas.ReviewModel, title_id: int):
    db_review = models.Review(
        content=review.content, 
        likes=0, 
        dislikes=0, 
        title_id=title_id
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def delete_review(db: Session, review_id: int):
    db_review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if db_review:
        db.delete(db_review)
        db.commit()
        return True
    return False

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
