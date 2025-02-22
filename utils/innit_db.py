from config.database import engine
from models.title import Title
from models.review import Review
from models.user import Users
from models.reaction import Reaction

def create_tables():
    Title.metadata.create_all(bind=engine)
    Review.metadata.create_all(bind=engine)
    Users.metadata.create_all(bind=engine)
    Reaction.metadata.create_all(bind=engine)
