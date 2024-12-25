from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from starlette import status
from service.user_service import UserService
from service.file_service import FileService
from service.email_service import EmailService
from schemas.user_schema import *
from schemas.token_schema import *
from utils.auth_utils import oauth2_bearer_user, oauth2_bearer_admin
from datetime import timedelta
import models.user

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
def register_user(register_user_request: RegisterUserRequest,
                  service: Annotated[UserService, Depends()],
                  email_service: Annotated[EmailService, Depends()],):
    new_user = service.register_user(register_user_request)
    try:
        activation_token = email_service.create_user_activation_token(new_user.id, timedelta(days=256*365))
        email_service.send_email(activation_token,
                                recipient_email = register_user_request.email,
                                recipient_username = register_user_request.username)
    except:
        service.delete_user(new_user.id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not send an email.")

@router.post("/account/activation", status_code=status.HTTP_200_OK)
def activation_token_verification(email_service: Annotated[EmailService, Depends()], activation_token: str = Query('')):
    return email_service.check_activation_token(activation_token)

@router.post("/reset/password/email")
def send_email_reset_password(email_service: Annotated[EmailService, Depends()],
                              service: Annotated[UserService, Depends()],
                              email: str = Query('')):
    try:
        user = service.get_user_by_email(email)
        reset_password_token = email_service.create_password_reset_token(user.id, timedelta(hours=2))
        email_service.send_reset_password_email(reset_password_token,
                                                recipient_email = user.email,
                                                recipient_username = user.username)
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not send an email.")

@router.post("/reset/password/token/verification", status_code=status.HTTP_200_OK)
def reset_password_token_verification(email_service: Annotated[EmailService, Depends()], reset_password_token: str = Query('')):
    return email_service.check_reset_password_token(reset_password_token)

@router.post("/reset/password", status_code=status.HTTP_200_OK)
def reset_password(email_service: Annotated[EmailService, Depends()],
                   service: Annotated[UserService, Depends()],
                   data: ResetPasswordRequest):
    try:
        user_id = email_service.check_reset_password_token(data.reset_password_token)
        service.reset_password(data.new_password, user_id)
        return {"detail": "password changed successfully"}
    except UserService.UserServiceException as error:
        raise HTTPException(status_code=500, detail=f'{error}')

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
