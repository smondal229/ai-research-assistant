from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, Text

from .database import Base


class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    # Gemini 004 uses 768 dimensions
    embedding = Column(Vector(768))
