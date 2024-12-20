from fastapi import Depends, APIRouter, Query
from typing import Annotated
from starlette import status
from schemas.reaction_schema import *
from service.reaction_service import ReactionService
from utils.auth_utils import oauth2_bearer_user, oauth2_bearer_user_optional
from models.user import Users


router = APIRouter(
    prefix="/reaction"
)

@router.post("", status_code=status.HTTP_204_NO_CONTENT)
def process_reaction(current_user: Annotated[str, Depends(oauth2_bearer_user)], service: Annotated[ReactionService, Depends()], reaction: ReactionRequest):
    service.process_reaction(current_user.id, reaction)

@router.get("/count", status_code=status.HTTP_200_OK, response_model=ReactionsCountResponse)
def get_reactions(service: Annotated[ReactionService, Depends()],
                  current_user: Annotated[Users | None, Depends(oauth2_bearer_user_optional)] = None,
                  title_ids: list[int] = Query([]),
                  review_ids: list[int] = Query([])):
    if title_ids:
        return service.count_title_reactions(title_ids, current_user)
    elif review_ids:
        return service.count_review_reactions(review_ids, current_user)
