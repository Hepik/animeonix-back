from models.reaction import ReactionTypeEnum
from pydantic import BaseModel
from typing import Optional, List


class ReactionRequest(BaseModel):
    title_id: Optional[int] = None
    review_id: Optional[int] = None
    type: ReactionTypeEnum

class ReactionCountResponse(BaseModel):
    title_id: Optional[int] = None
    review_id: Optional[int] = None
    current_user_reaction: ReactionTypeEnum | None
    likes: int
    dislikes: int

class ReactionsCountResponse(BaseModel):
    reactions: List[ReactionCountResponse]
    
    class Config:
        from_attributes = True
