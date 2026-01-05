"""
Vector Database Operations
Pure database operations - NO SETUP CODE!
Assumes database is already migrated.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, PointStruct
import google.generativeai as genai
import os

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

class VectorStore:
    """
    Vector database operations for research documents

    IMPORTANT: Run migrations/init_qdrant.py BEFORE using this class!
    """

    def __init__(self, collection_name="research_documents", use_docker=True):
        """
        Initialize connection to existing vector database

        Args:
            collection_name: Name of the collection (must already exist!)
            use_docker: Whether to connect to Docker or use local storage
        """
        if use_docker:
            self.client = QdrantClient(host="localhost", port=6333, timeout=60)
        else:
            self.client = QdrantClient(path="./qdrant_data")

        self.collection_name = collection_name

        # Verify collection exists
        self._verify_collection()

    def _verify_collection(self):
        """Verify that the collection exists"""
        try:
            collections = {c.name for c in self.client.get_collections().collections}

            if self.collection_name not in collections:
                raise RuntimeError(
                    f"❌ Collection '{self.collection_name}' does not exist!\n"
                    f"💡 Run migration first: python migrations/init_qdrant.py"
                )

            print(f"✅ Connected to collection: {self.collection_name}")
        except Exception as e:
            print(f"❌ Failed to verify collection: {e}")
            raise

    def _get_embedding(self, text, task_type="retrieval_document"):
        """Generate embedding using Gemini"""
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type=task_type
        )
        return result['embedding']

    def add_document(self, doc_id, text, metadata=None):
        """Add a document to the vector store"""
        embedding = self._get_embedding(text, task_type="retrieval_document")

        payload = {"text": text, "doc_id": doc_id}
        if metadata:
            payload.update(metadata)

        point = PointStruct(
            id=hash(doc_id) % (10 ** 8),
            vector=embedding,
            payload=payload
        )

        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

        return {"status": "success", "doc_id": doc_id}

    def search(self, query, top_k=5, filters=None):
        """Search for similar documents"""
        query_embedding = self._get_embedding(query, task_type="retrieval_query")

        search_filter = None
        if filters:
            search_filter = Filter(
                must=[
                    FieldCondition(key=k, match=MatchValue(value=v))
                    for k, v in filters.items()
                ]
            )

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=search_filter
        )

        return [
            {
                "doc_id": hit.payload["doc_id"],
                "text": hit.payload["text"],
                "score": hit.score,
                "metadata": {k: v for k, v in hit.payload.items()
                           if k not in ["doc_id", "text"]}
            }
            for hit in results
        ]

    def delete_document(self, doc_id):
        """Delete a document"""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=[hash(doc_id) % (10 ** 8)]
        )
        return {"status": "deleted", "doc_id": doc_id}

    def get_stats(self):
        """Get collection statistics"""
        info = self.client.get_collection(self.collection_name)
        return {
            "name": info.name,
            "vectors_count": info.points_count,
            "vector_size": info.config.params.vectors.size,
            "distance_metric": str(info.config.params.vectors.distance)
        }
