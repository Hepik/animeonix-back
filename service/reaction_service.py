from fastapi import HTTPException, Depends
from schemas.reaction_schema import *
from repository.reaction_repository import ReactionRepository
from typing import Annotated
from starlette import status

class ReactionService:
    def __init__(self, repository: Annotated[ReactionRepository, Depends()]):
        self.repository = repository

    def process_reaction(self, user_id: int, reaction: ReactionRequest):
        if reaction.title_id:
            existing_reaction = self.repository.get_reaction_by_title_id(user_id, reaction.title_id)
        elif reaction.review_id:
            existing_reaction = self.repository.get_reaction_by_review_id(user_id, reaction.review_id)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reaction not found")
        
        if existing_reaction:
            if existing_reaction.type == reaction.type:
                self.repository.delete_reaction(existing_reaction)
            else:
                existing_reaction.type = reaction.type
                self.repository.update_reaction(existing_reaction)
        else:
            return self.repository.create_reaction(user_id, reaction)
