from urllib import response
from fastapi import HTTPException, Depends
from schemas.reaction_schema import *
from repository.reaction_repository import ReactionRepository
from typing import Annotated
from starlette import status
from models.user import Users

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

    def count_title_reactions(self, title_ids: list[int], current_user: Users | None = None):
        reactions = self.repository.get_reaction_by_title_ids(title_ids)

        reactions_counts_per_title = {}
        for reaction in reactions:
            if reaction.title_id not in reactions_counts_per_title:
                reactions_counts_per_title[reaction.title_id] = {
                    'title_id': reaction.title_id,
                    'current_user_reaction': None,
                    'likes': 0,
                    'dislikes': 0,
                }
            if current_user and current_user.id == reaction.user_id:
                reactions_counts_per_title[reaction.title_id]['current_user_reaction'] = reaction.type
            if reaction.type.value == "like":
                reactions_counts_per_title[reaction.title_id]['likes'] += 1
            else:
                reactions_counts_per_title[reaction.title_id]['dislikes'] += 1
        response = {
            "reactions": list(reactions_counts_per_title.values())
        }
        return response
    
    def count_review_reactions(self, review_ids: list[int], current_user: Users | None = None):
        reactions = self.repository.get_reaction_by_review_ids(review_ids)

        reactions_counts_per_review = {}
        for reaction in reactions:
            if reaction.review_id not in reactions_counts_per_review:
                reactions_counts_per_review[reaction.review_id] = {
                    'review_id': reaction.review_id,
                    'user_id': reaction.user_id,
                    'current_user_reaction': None,
                    'likes': 0,
                    'dislikes': 0,
                }
            if current_user and current_user.id == reaction.user_id:
                reactions_counts_per_review[reaction.review_id]['current_user_reaction'] = reaction.type
            if reaction.type.value == "like":
                reactions_counts_per_review[reaction.review_id]['likes'] += 1
            else:
                reactions_counts_per_review[reaction.review_id]['dislikes'] += 1
        response = {
            "reactions": list(reactions_counts_per_review.values())
        }
        return response
