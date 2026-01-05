import google.generativeai as genai
from sqlalchemy import select

from .models import Document


def get_embedding(text: str):
    """Generates a vector for the given text."""
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_query"
    )
    return result['embedding']

def vector_search(session, query_text: str, limit: int = 3):
    """Standard vector search logic."""
    query_vector = get_embedding(query_text)

    stmt = select(Document.content).order_by(
        Document.embedding.cosine_distance(query_vector)
    ).limit(limit)

    return session.execute(stmt).scalars().all()
