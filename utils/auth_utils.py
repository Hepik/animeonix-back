from fastapi.security import OAuth2PasswordBearer
from service.user_service import UserService
from typing import Annotated
from fastapi import HTTPException, Depends
from starlette import status

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

def oauth2_bearer_admin(token: Annotated[str, Depends(oauth2_bearer)], service: Annotated[UserService, Depends()]):
    user = service.get_current_user(token)
    if not user or user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. Admin role required.")
    
    return user

def oauth2_bearer_user(token: Annotated[str, Depends(oauth2_bearer)], service: Annotated[UserService, Depends()]):
    user = service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. Authentication required.")
    
    return user
