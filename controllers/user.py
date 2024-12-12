from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from starlette import status
from service.user_service import UserService
from service.file_service import FileService
from schemas.user_schema import *
from schemas.token_schema import *
from utils.auth_utils import oauth2_bearer_user, oauth2_bearer_admin

router = APIRouter(
    prefix="/users"
)


@router.get("", response_model=UsersResponse)
def get_users(
        service: Annotated[UserService, Depends()],
        page: int = Query(1), 
        limit: int = Query(10),
        username: str = Query(''),
        id: int = Query(None),
    ):
    return service.get_users(page, limit, username, id)

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
def partial_update_user(_: Annotated[str, Depends(oauth2_bearer_admin)], id: int, user: UserUpdate, service: Annotated[UserService, Depends()]):
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

@router.post("/change/avatar", status_code=200)
def upload_avatar(
    current_user: Annotated[str, Depends(oauth2_bearer_user)],
    user_service: Annotated[UserService, Depends()],
    file_service: Annotated[FileService, Depends()],
    file: UploadFile = File(...),
    
):
    try:
        user = file_service.process_avatar(current_user.avatar, file)

        user_service.partial_update_user(current_user.id, user)
        
        return {"detail": "Avatar updated successfully", "filename": user.avatar}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading avatar: {str(e)}")
