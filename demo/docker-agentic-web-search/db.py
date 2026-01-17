from sqlalchemy import create_engine, Column, Integer, Text, DateTime , Float, String
from sqlalchemy.orm import declarative_base, sessionmaker
from pgvector.sqlalchemy import Vector

DATABASE_URL = "postgresql://postgres:postgres@demo-pgvector-1:5432/ics"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class Document(Base):
    __tablename__ = "web_search_documents"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768))  # nomic-embed-text = 768 dims
    topic = Column(Text, index=True)
    url = Column(Text)
    published_at = Column(DateTime)
    sentiment = Column(Float)   # -1.0 to +1.0
     
def init_db():
    Base.metadata.create_all(bind=engine)
