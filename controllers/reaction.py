from fastapi import Depends, APIRouter
from typing import Annotated
from starlette import status
from schemas.reaction_schema import *
from service.reaction_service import ReactionService
from utils.auth_utils import oauth2_bearer_user


router = APIRouter(
    prefix="/reaction"
)

@router.post("", status_code=status.HTTP_204_NO_CONTENT)
def process_reaction(current_user: Annotated[str, Depends(oauth2_bearer_user)], service: Annotated[ReactionService, Depends()], reaction: ReactionRequest):
    service.process_reaction(current_user.id, reaction)
