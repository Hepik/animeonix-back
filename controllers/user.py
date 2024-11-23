from typing import Annotated
from fastapi import APIRouter, Depends
from starlette import status
from service.user_service import UserService
from schemas.user_schema import *
from schemas.token_schema import *
from utils.auth_utils import oauth2_bearer_user, oauth2_bearer_admin

router = APIRouter(
    prefix="/users"
)


@router.get("", response_model=UsersResponse)
def get_users(_: Annotated[str, Depends(oauth2_bearer_admin)], service: Annotated[UserService, Depends()]):
    return service.get_users()

@router.get("/current", status_code=status.HTTP_200_OK)
def user(user: Annotated[dict, Depends(UserService.get_current_user)]):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')
    return {"User": user}

@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(_: Annotated[str, Depends(oauth2_bearer_admin)], create_user_request: CreateUserRequest, service: Annotated[UserService, Depends()]):
    service.create_user(create_user_request)

@router.patch("/{id}", response_model=Response)
def partial_update_user(_: Annotated[str, Depends(oauth2_bearer_user)], id: int, user: UserUpdate, service: Annotated[UserService, Depends()]):
    return service.partial_update_user(id=id, user=user)

@router.delete("/{id}", response_model=DeleteResponse)
def delete_user(_: Annotated[str, Depends(oauth2_bearer_admin)], id: int, service: Annotated[UserService, Depends()]):
    service.delete_user(id=id)
    return {"detail": "User deleted successfully"}
