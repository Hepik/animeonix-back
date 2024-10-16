from fastapi import Depends, HTTPException, Query, APIRouter
from sqlalchemy.orm import Session
from schemas.title_schema import *
from service.title_service import TitleService
from config.database import get_db


router = APIRouter(
    prefix="/titles"
)


@router.get("", response_model=TitleResponse)
def get_titles(page: int = Query(1), limit: int = Query(10), db: Session = Depends(get_db)):
    _service = TitleService(db)
    return _service.get_titles(page=page, limit=limit)
    

@router.get("/{slug}", response_model=Title)
def get_title_by_slug(slug: str, db: Session = Depends(get_db)):
    _service = TitleService(db)
    title = _service.get_title_by_slug(slug=slug)
    if not title:
        raise HTTPException(status_code=404, detail="Title not found")
    return title


@router.post("", response_model=Title)
def create_title(title: TitleCreate, db: Session = Depends(get_db)):
    _service = TitleService(db)
    return _service.create_title(title=title)


@router.put("/{title_id}", response_model=Title)
def update_title(title_id: int, title: TitleCreate, db: Session = Depends(get_db)):
    _service = TitleService(db)
    return _service.update_title(title_id=title_id, title=title)


@router.patch("/{title_id}", response_model=Title)
def partial_update_title(title_id: int, title: TitleUpdate, db: Session = Depends(get_db)):
    _service = TitleService(db)
    return _service.partial_update_title(title_id=title_id, title=title)


@router.delete("/{title_id}", response_model=DeleteResponse)
def delete_title(title_id: int, db: Session = Depends(get_db)):
    _service = TitleService(db)
    _service.delete_title(title_id=title_id)
    return {"detail": "Title deleted successfully"}
