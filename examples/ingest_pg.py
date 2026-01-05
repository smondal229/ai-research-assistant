"""
Example ingestion script for Postgres + pgvector.
Usage: python examples/ingest_pg.py "This is the document text..."
"""

import sys

from src.database import SessionLocal
from src.models import Document
from src.services import get_embedding


def main(text: str):
    embedding = get_embedding(text)

    with SessionLocal() as session:
        doc = Document(content=text, embedding=embedding)
        session.add(doc)
        session.commit()
        print(f"Inserted document id={doc.id}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python examples/ingest_pg.py '<text>'")
        sys.exit(1)

    text = sys.argv[1]
    main(text)
