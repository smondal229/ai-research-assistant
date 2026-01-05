# AI Research Assistant ⚡️

**One-liner:** ScholarAI is a memory-enabled, vector-backed research assistant that ingests documents, stores embeddings in PostgreSQL using the `pgvector` extension, and uses Google Gemini (or other configured LMs) to answer contextual queries and assist with research workflows.

---

## 🚀 Quick overview

- Ingest documents and papers into PostgreSQL (using the `pgvector` extension)
- Store metadata and small structured data in PostgreSQL
- Use a Gemini-powered agent (or other LMs) that consults the knowledge base via a tool
- Example entry points: `agent_with_memory.py` (simple local demo) and `python -m src.main` (interactive agent with knowledge search)

---

## ✅ Prerequisites

- Python 3.10+ installed
- Docker & Docker Compose (recommended)
- A Gemini / Google Generative API key (set as `GEMINI_API_KEY` in `.env`)

---

## 🛠️ Setup (local development)

1. Clone the repo and change directory

```bash
git clone <repo-url>
cd ai-research-assistant
```

2. Create a `.env` file from the sample and update values

Windows PowerShell:

```powershell
copy .env.sample .env
# then edit .env to add your GEMINI_API_KEY and confirm Postgres settings
```

3. Start Postgres (and any other services) using Docker Compose

```bash
docker-compose up -d
```

4. Enable `pgvector` in Postgres

This project uses `pgvector` inside PostgreSQL to store and search embeddings. If you started Postgres using `docker-compose` (the `pgvector/pgvector:pg16` image is used in this repo), you can enable the `vector` extension either from inside the container or by running the provided migration script.

From your host, enable `vector` using psql in the running container:

```bash
# enter the postgres container (example using the default service name 'postgres')
docker-compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

Or run the included init script (recommended):

```bash
python migrations/init_pgvector.py
```

This will ensure the `vector` extension exists and is ready for use by the SQLAlchemy models.

5. Create a Python virtual environment and install dependencies

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

6. Enable pgvector extension and run migrations

```bash
python migrations/init_pgvector.py
```

The script ensures the `vector` extension is enabled. Your SQLAlchemy models (e.g., `src.models.Document`) will be created when you run `python -m src.main` which calls `Base.metadata.create_all(engine)`.

7. Run the project

- Minimal demo (conversation & memory demo):

```bash
python agent_with_memory.py
```

- Full interactive agent (creates DB tables and uses `search_knowledge_base` tool):

```bash
python -m src.main
```

> `src.main` will call `Base.metadata.create_all(engine)` to ensure DB tables exist for SQLAlchemy models.

---

## 📚 How to add/search documents (example)

Use the SQLAlchemy `Document` model and the `services` helpers to add/search documents using `pgvector`.

Example (run from project root):

```bash
python - <<'PY'
import sys
sys.path.append('.')
from src.database import SessionLocal
from src.models import Document
from src.services import get_embedding, vector_search

text = 'This is an example research document about neural networks.'
embedding = get_embedding(text)

with SessionLocal() as session:
    doc = Document(content=text, embedding=embedding)
    session.add(doc)
    session.commit()
    print(f'Inserted document id={doc.id}')

# Run a vector search
with SessionLocal() as session:
    results = vector_search(session, 'neural networks')
    print(results)
PY
```

This uses Gemini embeddings (configured with `GEMINI_API_KEY`) and stores vectors in the `embedding` column (pgvector).

---

## 🔌 How the pieces fit together

- `src/models.py` — SQLAlchemy `Document` model with an `embedding` column (uses `pgvector` via `pgvector.sqlalchemy.Vector`).
- `migrations/init_pgvector.py` — ensures the `vector` extension exists in Postgres.
- `src/services.py` — contains embedding generation and vector search logic (uses Gemini embedding model `text-embedding-004`).
- `src/tools.py` — exposes the `search_knowledge_base` tool used by the agent.
- `src/main.py` — example interactive agent that uses tools and starts a chat loop.
- `agent_with_memory.py` — small demo of a conversation agent that keeps local conversation history.

---

## ⚠️ Troubleshooting

- Failed to connect to Postgres:
  - Check `docker-compose logs postgres` and your `.env` `POSTGRES_*` variables.
  - Ensure port 5432 is free and Docker container is healthy.

- `pgvector` / extension errors:
  - Ensure the Postgres container is running and the `vector` extension is enabled (run `python migrations/init_pgvector.py` or create the extension via psql inside the container).

- Embeddings / Gemini errors:
  - Ensure `GEMINI_API_KEY` is set in `.env` and valid.

---

## 💡 Tips & next steps

- Add a small ingestion script to batch-process PDFs or text files and push them into the database.
- Add tests for the `services` embedding/search behavior.
- (Optional) Add automated DB initialization to your `docker-compose` workflows to ensure the `vector` extension exists at startup.

---

## Contributing

Contributions welcome — please open PRs with small, focused changes. Add tests when you can and update the README when behavior changes.

---

## License & Credits

This project is provided as-is. Add your preferred LICENSE file if you want to share it publicly.

---

If you'd like, I can also:
- Add an `examples/` script to demonstrate ingestion and a simple query flow ✅
- Add a `docker-compose` service for Qdrant so both Postgres and Qdrant start together ✅
- Create a simple badge-style header and short `CONTRIBUTING.md` ✍️

Which of these should I do next?
