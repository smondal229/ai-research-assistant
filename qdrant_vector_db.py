
# import os

# import google.generativeai as genai
# from dotenv import load_dotenv
# from qdrant_client import QdrantClient
# from qdrant_client.models import (Distance, FieldCondition, Filter, MatchValue,
#                                   PointStruct, VectorParams)

# load_dotenv()
# api_key = os.getenv("GEMINI_API_KEY")
# genai.configure(api_key=api_key)

# class QdrantVectorDB:
#     def __init__(self, collection_name="research_documents", use_docker=True):
#         """
#         Initialize Qdrant vector database

#         Args:
#             collection_name: Name of the collection to use
#             use_docker: If True, connect to Docker instance. If False, use local storage
#         """
#         print("🚀 Initializing Qdrant Vector Database...")

#         # Connect to Qdrant
#         if use_docker:
#             # For Docker: connect via host and port
#             self.client = QdrantClient(host="localhost", port=6333)
#             print("📡 Connected to Qdrant Docker instance")
#         else:
#             # For local storage: no Docker needed
#             self.client = QdrantClient(path="./qdrant_data")
#             print("💾 Using local Qdrant storage")

#         self.collection_name = collection_name

#         # Create collection if it doesn't exist
#         self._create_collection()

#         print("✅ Qdrant ready!\n")

#     def _create_collection(self):
#         """Create a collection with proper configuration"""
#         try:
#             # Check if collection exists
#             collections = self.client.get_collections().collections
#             exists = any(c.name == self.collection_name for c in collections)

#             if not exists:
#                 print(f"📦 Creating collection '{self.collection_name}'...")

#                 # Create collection with vector configuration
#                 self.client.create_collection(
#                     collection_name=self.collection_name,
#                     vectors_config=VectorParams(
#                         size=768,  # Gemini text-embedding-004 produces 768-dimensional vectors
#                         distance=Distance.COSINE  # Cosine similarity for measuring distance
#                     )
#                 )
#                 print(f"✅ Collection '{self.collection_name}' created!")
#             else:
#                 print(f"📂 Collection '{self.collection_name}' already exists")

#         except Exception as e:
#             print(f"❌ Error creating collection: {e}")
#             raise
#     def _get_embedding(self, text, task_type="retrieval_document"):
#         """
#         Generate embedding using Gemini's embedding API

#         Args:
#             text: Text to convert to embedding
#             task_type: Type of task ('retrieval_document' for storing, 'retrieval_query' for searching)

#         Returns:
#             List of 768 float values representing the embedding
#         """
#         try:
#             result = genai.embed_content(
#                 model="models/text-embedding-004",  # Latest Gemini embedding model
#                 content=text,
#                 task_type=task_type
#             )
#             return result['embedding']
#         except Exception as e:
#             print(f"❌ Error generating embedding: {e}")
#             raise

#     def add_document(self, doc_id, text, metadata=None):
#         """
#         Add a document with metadata to Qdrant

#         Args:
#             doc_id: Unique identifier for the document
#             text: The document text content
#             metadata: Dictionary of additional metadata (topic, year, author, etc.)
#         """
#         print(f"📝 Adding document: {doc_id}")

#         try:
#             # Generate embedding for the document
#             embedding = self._get_embedding(text, task_type="retrieval_document")

#             # Prepare payload (metadata + text)
#             payload = {
#                 "text": text,
#                 "doc_id": doc_id
#             }
#             if metadata:
#                 payload.update(metadata)

#             # Create point
#             point = PointStruct(
#                 id=hash(doc_id) % (10 ** 8),  # Convert string ID to integer
#                 vector=embedding,
#                 payload=payload
#             )

#             # Upload to Qdrant
#             self.client.upsert(
#                 collection_name=self.collection_name,
#                 points=[point]
#             )

#             print(f"✅ Document '{doc_id}' stored successfully!")
#             if metadata:
#                 print(f"   Metadata: {metadata}")
#             print()

#         except Exception as e:
#             print(f"❌ Error adding document '{doc_id}': {e}")
#             raise

#     def add_documents_batch(self, documents):
#         """
#         Add multiple documents at once (more efficient)

#         Args:
#             documents: List of dictionaries with 'doc_id', 'text', and optional 'metadata'
#         """
#         print(f"📦 Adding {len(documents)} documents in batch...")

#         try:
#             points = []

#             for doc in documents:
#                 doc_id = doc['doc_id']
#                 text = doc['text']
#                 metadata = doc.get('metadata', {})

#                 # Generate embedding
#                 embedding = self._get_embedding(text, task_type="retrieval_document")

#                 # Prepare payload
#                 payload = {
#                     "text": text,
#                     "doc_id": doc_id
#                 }
#                 payload.update(metadata)

#                 # Create point
#                 point = PointStruct(
#                     id=hash(doc_id) % (10 ** 8),
#                     vector=embedding,
#                     payload=payload
#                 )
#                 points.append(point)

#             # Upload all at once
#             self.client.upsert(
#                 collection_name=self.collection_name,
#                 points=points
#             )

#             print(f"✅ Successfully added {len(documents)} documents!\n")

#         except Exception as e:
#             print(f"❌ Error adding documents in batch: {e}")
#             raise

#     def search(self, query, top_k=3, filter_conditions=None):
#         """
#         Search for similar documents with optional filtering

#         Args:
#             query: Search query text
#             top_k: Number of results to return
#             filter_conditions: Dictionary of metadata filters (e.g., {'year': 2024, 'topic': 'AI'})

#         Returns:
#             List of search results
#         """
#         print(f"🔍 Searching for: '{query}'")

#         try:
#             # Generate query embedding (note: different task_type!)
#             query_embedding = self._get_embedding(query, task_type="retrieval_query")

#             # Prepare filter if provided
#             search_filter = None
#             if filter_conditions:
#                 search_filter = Filter(
#                     must=[
#                         FieldCondition(
#                             key=key,
#                             match=MatchValue(value=value)
#                         )
#                         for key, value in filter_conditions.items()
#                     ]
#                 )
#                 print(f"   With filters: {filter_conditions}")

#             print(f"   Looking for top {top_k} results...\n")

#             # Search
#             results = self.client.search(
#                 collection_name=self.collection_name,
#                 query_vector=query_embedding,
#                 limit=top_k,
#                 query_filter=search_filter
#             )

#             # Display results
#             print("📊 Search Results:")
#             print("=" * 70)

#             if not results:
#                 print("No results found.")

#             for i, hit in enumerate(results, 1):
#                 print(f"\n{i}. Document ID: {hit.payload['doc_id']}")
#                 print(f"   Similarity Score: {hit.score:.4f} (higher = more similar)")
#                 print(f"   Text: {hit.payload['text'][:150]}...")

#                 # Show metadata
#                 metadata_keys = [k for k in hit.payload.keys()
#                                if k not in ['text', 'doc_id']]
#                 if metadata_keys:
#                     metadata_str = ', '.join(f'{k}={hit.payload[k]}' for k in metadata_keys)
#                     print(f"   Metadata: {metadata_str}")

#             print("\n" + "=" * 70)
#             return results

#         except Exception as e:
#             print(f"❌ Error searching: {e}")
#             raise

#     def delete_document(self, doc_id):
#         """Delete a document by ID"""
#         try:
#             self.client.delete(
#                 collection_name=self.collection_name,
#                 points_selector=[hash(doc_id) % (10 ** 8)]
#             )
#             print(f"🗑️  Deleted document: {doc_id}")
#         except Exception as e:
#             print(f"❌ Error deleting document '{doc_id}': {e}")
#             raise

#     def get_collection_info(self):
#         """Get information about the collection"""
#         try:
#             info = self.client.get_collection(self.collection_name)
#             print(f"\n📊 Collection Information:")
#             print("=" * 50)
#             print(f"   Name: {info.name}")
#             print(f"   Total Vectors: {info.points_count}")
#             print(f"   Vector Dimensions: {info.config.params.vectors.size}")
#             print(f"   Distance Metric: {info.config.params.vectors.distance}")
#             print("=" * 50 + "\n")
#             return info
#         except Exception as e:
#             print(f"❌ Error getting collection info: {e}")
#             raise

#     def clear_collection(self):
#         """Delete all documents from the collection"""
#         try:
#             self.client.delete_collection(self.collection_name)
#             print(f"🗑️  Collection '{self.collection_name}' cleared!")
#             self._create_collection()  # Recreate empty collection
#         except Exception as e:
#             print(f"❌ Error clearing collection: {e}")
#             raise


# if __name__ == "__main__":
#     print("=" * 70)
#     print("QDRANT VECTOR DATABASE - DEMO")
#     print("=" * 70 + "\n")

#     # Initialize Qdrant (set use_docker=False if not using Docker)
#     db = QdrantVectorDB(use_docker=True)

#     # ========================================================================
#     # PART 1: Adding Individual Documents
#     # ========================================================================
#     print("\n" + "=" * 70)
#     print("PART 1: ADDING INDIVIDUAL DOCUMENTS")
#     print("=" * 70 + "\n")

#     db.add_document(
#         doc_id="ai_agents_intro",
#         text="Artificial intelligence agents are autonomous software systems that can perceive their environment, make decisions, and take actions to achieve specific goals. They use machine learning models to understand context and adapt their behavior based on feedback.",
#         metadata={
#             "topic": "AI Agents",
#             "source": "research_paper",
#             "year": 2024,
#             "difficulty": "intermediate",
#             "author": "AI Research Lab"
#         }
#     )

#     db.add_document(
#         doc_id="vector_db_guide",
#         text="Vector databases are specialized systems designed for storing and querying high-dimensional vectors. They enable semantic search by finding data points that are similar in meaning, not just matching keywords. This technology is crucial for modern AI applications like retrieval-augmented generation.",
#         metadata={
#             "topic": "Vector Databases",
#             "source": "technical_documentation",
#             "year": 2024,
#             "difficulty": "advanced",
#             "author": "Tech Corp"
#         }
#     )

#     db.add_document(
#         doc_id="ml_embeddings",
#         text="Machine learning embeddings are numerical representations of data that capture semantic meaning. Neural networks transform text, images, or other data into dense vectors where similar items are located close together in high-dimensional space. This enables powerful similarity search capabilities.",
#         metadata={
#             "topic": "Machine Learning",
#             "source": "tutorial",
#             "year": 2023,
#             "difficulty": "beginner",
#             "author": "ML Academy"
#         }
#     )

#     # ========================================================================
#     # PART 2: Batch Adding Documents
#     # ========================================================================
#     print("=" * 70)
#     print("PART 2: BATCH ADDING DOCUMENTS")
#     print("=" * 70 + "\n")

#     batch_documents = [
#         {
#             "doc_id": "rag_systems",
#             "text": "Retrieval-Augmented Generation combines large language models with information retrieval. The system retrieves relevant documents from a vector database and uses them as context for generating accurate, grounded responses. This approach significantly improves the quality and factuality of AI-generated content.",
#             "metadata": {
#                 "topic": "RAG",
#                 "source": "white_paper",
#                 "year": 2024,
#                 "difficulty": "advanced",
#                 "author": "OpenAI Research"
#             }
#         },
#         {
#             "doc_id": "python_basics",
#             "text": "Python is a versatile, high-level programming language widely used in data science, web development, and artificial intelligence. Its simple syntax, extensive standard library, and rich ecosystem of third-party packages make it ideal for rapid prototyping and production applications alike.",
#             "metadata": {
#                 "topic": "Programming",
#                 "source": "guide",
#                 "year": 2023,
#                 "difficulty": "beginner",
#                 "author": "Python Foundation"
#             }
#         },
#         {
#             "doc_id": "llm_overview",
#             "text": "Large Language Models are neural networks trained on vast amounts of text data to understand and generate human-like text. They can perform various tasks including translation, summarization, question answering, and creative writing. Recent advances have made them increasingly capable and accessible.",
#             "metadata": {
#                 "topic": "LLMs",
#                 "source": "research_paper",
#                 "year": 2024,
#                 "difficulty": "intermediate",
#                 "author": "AI Lab"
#             }
#         }
#     ]

#     db.add_documents_batch(batch_documents)

#     # ========================================================================
#     # PART 3: Collection Information
#     # ========================================================================
#     db.get_collection_info()

#     # ========================================================================
#     # PART 4: Semantic Search Tests
#     # ========================================================================
#     print("=" * 70)
#     print("PART 4: SEMANTIC SEARCH TESTS")
#     print("=" * 70 + "\n")

#     # Test 1: Basic semantic search
#     print("TEST 1: Basic Semantic Search")
#     print("-" * 70)
#     db.search("What are intelligent software systems?", top_k=3)

#     print("\n")

#     # Test 2: Search with filtering (only advanced topics)
#     print("TEST 2: Search with Metadata Filtering (Advanced Topics Only)")
#     print("-" * 70)
#     db.search(
#         "How do I implement semantic search?",
#         top_k=3,
#         filter_conditions={"difficulty": "advanced"}
#     )

#     print("\n")

#     # Test 3: Search by year
#     print("TEST 3: Search with Year Filter (2024 Only)")
#     print("-" * 70)
#     db.search(
#         "Recent AI developments",
#         top_k=3,
#         filter_conditions={"year": 2024}
#     )

#     print("\n")

#     # Test 4: Multi-condition filter
#     print("TEST 4: Multi-Condition Filter (2024 + Advanced)")
#     print("-" * 70)
#     db.search(
#         "AI technology",
#         top_k=2,
#         filter_conditions={"year": 2024, "difficulty": "advanced"}
#     )

#     print("\n")

#     # Test 5: Negative example (should find unrelated documents)
#     print("TEST 5: Unrelated Query (Should Find Different Results)")
#     print("-" * 70)
#     db.search("programming languages for beginners", top_k=2)

#     print("\n" + "=" * 70)
#     print("DEMO COMPLETE!")
#     print("=" * 70)
