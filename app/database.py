
from sqlmodel import create_engine, SQLModel, Session
from app.config import settings

DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL, echo=True)





def create_tables():
    from app.models import Post
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
