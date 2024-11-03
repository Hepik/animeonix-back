from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm
from service.user_service import UserService
from schemas.user_schema import *
from schemas.token_schema import *

router = APIRouter(
    prefix="/auth"
)


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], service: Annotated[UserService, Depends()]):
    user = service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
    token = service.create_access_token(user.username, user.id, timedelta(hours=10))

    return {'access_token': token, 'token_type': 'bearer'}
