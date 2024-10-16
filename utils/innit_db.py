from config.database import engine
from models.title import Title
from models.review import Review

def create_tables():
    Title.metadata.create_all(bind=engine)
    Review.metadata.create_all(bind=engine)
