from models.reaction import ReactionTypeEnum
from pydantic import BaseModel
from typing import Optional


class ReactionRequest(BaseModel):
    title_id: Optional[int] = None
    review_id: Optional[int] = None
    type: ReactionTypeEnum
