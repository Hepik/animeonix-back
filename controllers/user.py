from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status
from service.user_service import UserService
from schemas.user_schema import *
from schemas.token_schema import *
from utils.auth_utils import oauth2_bearer_user, oauth2_bearer_admin

router = APIRouter(
    prefix="/users"
)


@router.get("", response_model=UsersResponse)
def get_users(
        _: Annotated[str, Depends(oauth2_bearer_user)], 
        service: Annotated[UserService, Depends()], 
        username: str = Query('')
    ):
    return service.get_users(username)

@router.get("/current", status_code=status.HTTP_200_OK, response_model=Response)
def get_current_user(current_user: Annotated[str, Depends(oauth2_bearer_user)]):
    return current_user

@router.post("/register", status_code=status.HTTP_200_OK)
def register_user(register_user_request: RegisterUserRequest, service: Annotated[UserService, Depends()]):
    service.register_user(register_user_request)

@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(_: Annotated[str, Depends(oauth2_bearer_admin)], create_user_request: CreateUserRequest, service: Annotated[UserService, Depends()]):
    service.create_user(create_user_request)

@router.patch("/{id}", response_model=Response)
def partial_update_user(_: Annotated[str, Depends(oauth2_bearer_user)], id: int, user: UserUpdate, service: Annotated[UserService, Depends()]):
    return service.partial_update_user(id=id, user=user)

@router.patch("/change/password", status_code=status.HTTP_200_OK)
def change_password(current_user: Annotated[str, Depends(oauth2_bearer_user)], 
    data: PasswordChangeRequest, service: Annotated[UserService, Depends()]):
    try:
        service.change_password(current_user, current_password=data.current_password, new_password=data.new_password)
        return {"detail": "password changed successfully"}
    except UserService.UserServiceException as error:
        raise HTTPException(status_code=500, detail=f'{error}')

@router.delete("/{id}", response_model=DeleteResponse)
def delete_user(_: Annotated[str, Depends(oauth2_bearer_admin)], id: int, service: Annotated[UserService, Depends()]):
    service.delete_user(id=id)
    return {"detail": "User deleted successfully"}
