from .database import SessionLocal
from .services import vector_search


def search_knowledge_base(query: str) -> str:
    """Useful for finding information in the local research database."""
    with SessionLocal() as session:
        results = vector_search(session, query)
        if not results:
            return "No relevant information found in the database."
        return "\n\n".join(results)
