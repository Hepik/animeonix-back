import models.reaction
import schemas.reaction_schema
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from config.database import get_db


class ReactionRepository:
    def __init__(self, session: Annotated[Session, Depends(get_db)]):
        self.db = session

    def get_reaction_by_title_id(self, user_id: int, title_id: int):
        return self.db.query(models.reaction.Reaction).filter_by(title_id=title_id, user_id=user_id).first()
    
    def get_reaction_by_review_id(self, user_id: int, review_id: int):
        return self.db.query(models.reaction.Reaction).filter_by(review_id=review_id, user_id=user_id).first()

    def delete_reaction(self, reaction: models.reaction.Reaction):
        self.db.delete(reaction)
        self.db.commit()
        return True
    
    def update_reaction(self, existing_reaction: models.reaction.Reaction):
        self.db.commit()
        self.db.refresh(existing_reaction)
        return True

    def create_reaction(self, user_id: int, reaction: schemas.reaction_schema.ReactionRequest):
        new_reaction = models.reaction.Reaction(title_id=reaction.title_id,
                                                review_id=reaction.review_id,
                                                user_id=user_id,
                                                type=reaction.type
                                                )
        self.db.add(new_reaction)
        self.db.commit()
        self.db.refresh(new_reaction)
        return new_reaction

    def get_reaction_by_title_ids(self, title_ids: list[int]):
        return self.db.query(models.reaction.Reaction).where(models.reaction.Reaction.title_id.in_(title_ids))
    
    def get_reaction_by_review_ids(self, review_ids: list[int]):
        return self.db.query(models.reaction.Reaction).where(models.reaction.Reaction.review_id.in_(review_ids))
