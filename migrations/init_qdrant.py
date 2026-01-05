"""
Qdrant Database Migration Script
Run this ONCE to set up your database schema
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import sys

def migrate_qdrant():
    """Initialize Qdrant database with required collections"""

    print("=" * 70)
    print("QDRANT DATABASE MIGRATION")
    print("=" * 70 + "\n")

    # Connect to Qdrant
    print("📡 Connecting to Qdrant...")
    try:
        client = QdrantClient(host="localhost", port=6333, timeout=60)
        print("✅ Connected to Qdrant\n")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        print("💡 Make sure Qdrant is running: docker-compose up -d")
        sys.exit(1)

    # List of collections to create
    collections_config = [
        {
            "name": "research_documents",
            "vector_size": 768,
            "distance": Distance.COSINE,
            "description": "Stores research documents and papers"
        },
        {
            "name": "agent_memory",
            "vector_size": 768,
            "distance": Distance.COSINE,
            "description": "Stores agent conversation history and context"
        },
        {
            "name": "code_snippets",
            "vector_size": 768,
            "distance": Distance.COSINE,
            "description": "Stores code examples and documentation"
        }
    ]

    # Get existing collections
    existing_collections = {c.name for c in client.get_collections().collections}
    print(f"📋 Found {len(existing_collections)} existing collections\n")

    # Create each collection
    for config in collections_config:
        collection_name = config["name"]

        if collection_name in existing_collections:
            print(f"⏭️  Skipping '{collection_name}' (already exists)")
            continue

        print(f"📦 Creating collection: {collection_name}")
        print(f"   Description: {config['description']}")
        print(f"   Vector size: {config['vector_size']}")
        print(f"   Distance metric: {config['distance']}")

        try:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=config["vector_size"],
                    distance=config["distance"]
                )
            )
            print(f"✅ Created '{collection_name}'\n")
        except Exception as e:
            print(f"❌ Failed to create '{collection_name}': {e}\n")

    # Summary
    print("=" * 70)
    print("MIGRATION SUMMARY")
    print("=" * 70)

    final_collections = client.get_collections().collections
    for collection in final_collections:
        info = client.get_collection(collection.name)
        print(f"\n📊 {collection.name}:")
        print(f"   Vectors: {info.points_count}")
        print(f"   Dimensions: {info.config.params.vectors.size}")
        print(f"   Distance: {info.config.params.vectors.distance}")

    print("\n" + "=" * 70)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 70 + "\n")

def rollback_qdrant():
    """Delete all collections (DANGEROUS - use with caution!)"""

    print("⚠️  WARNING: This will delete ALL collections!")
    response = input("Are you sure? Type 'yes' to confirm: ")

    if response.lower() != 'yes':
        print("❌ Rollback cancelled")
        return

    print("\n🗑️  Rolling back database...\n")

    client = QdrantClient(host="localhost", port=6333, timeout=60)
    collections = client.get_collections().collections

    for collection in collections:
        print(f"🗑️  Deleting collection: {collection.name}")
        client.delete_collection(collection.name)

    print("\n✅ Rollback complete - all collections deleted\n")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_qdrant()
    else:
        migrate_qdrant()
