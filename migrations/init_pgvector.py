"""
Postgres (pgvector) initialization script
Run this once to enable the `vector` extension required by pgvector.
"""

from src.database import engine


def init_pgvector():
    print("=" * 70)
    print("PGVECTOR INIT: enabling 'vector' extension if needed")
    print("=" * 70 + "\n")

    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector;")
            print("✅ 'vector' extension is enabled.")
    except Exception as e:
        print(f"❌ Failed to enable extension: {e}")
        print("💡 Make sure Postgres is running (docker-compose up -d) and your .env is configured correctly.")
        raise


if __name__ == '__main__':
    init_pgvector()
