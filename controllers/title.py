from fastapi import Depends, HTTPException, Query, APIRouter, UploadFile, File, Form
from typing import Annotated
from starlette import status
from schemas.title_schema import *
from service.title_service import TitleService
from service.file_service import FileService
from utils.auth_utils import oauth2_bearer_admin


router = APIRouter(
    prefix="/titles"
)


@router.get("", response_model=TitleResponse)
def get_titles(service: Annotated[TitleService, Depends()], page: int = Query(1), limit: int = Query(10), name: str = Query('')):
    return service.get_titles(page=page, limit=limit, name=name)
    

@router.get("/{slug}", response_model=Title)
def get_title_by_slug(slug: str, service: Annotated[TitleService, Depends()]):
    title = service.get_title_by_slug(slug=slug)
    if not title:
        raise HTTPException(status_code=404, detail="Title not found")
    return title


@router.post("", status_code=status.HTTP_201_CREATED)
def create_title(_: Annotated[str, Depends(oauth2_bearer_admin)], title: TitleCreate, service: Annotated[TitleService, Depends()]):
    return service.create_title(title=title)


@router.patch("/{id}", response_model=Title)
def partial_update_title(_: Annotated[str, Depends(oauth2_bearer_admin)], id: int, title: TitleUpdate, service: Annotated[TitleService, Depends()]):
    return service.partial_update_title(id=id, title=title)


@router.delete("/{id}", response_model=DeleteResponse)
def delete_title(_: Annotated[str, Depends(oauth2_bearer_admin)], id: int, service: Annotated[TitleService, Depends()]):
    service.delete_title(id=id)
    return {"detail": "Title deleted successfully"}


@router.post("/change/image", status_code=200)
def upload_image(_: Annotated[str, Depends(oauth2_bearer_admin)],
                file_service: Annotated[FileService, Depends()],
                file: UploadFile = File(...),
                old_image: str = Form(...),
                ):
    return file_service.process_image(old_image, file)
