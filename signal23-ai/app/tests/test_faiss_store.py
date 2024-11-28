import sys
from pathlib import Path
import shutil

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from app.src.rag.faiss_store import FAISSVectorStore
from app.src.data.embeddings import get_embeddings_model
from langchain_core.documents import Document

def test_store_persistence():
    """Test store persistence"""
    # Clean up any existing test data
    test_dir = Path("data/band_docs")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    print("\nTesting FAISS store persistence...")
    
    # Create initial documents
    docs = [
        Document(
            page_content="Test document one",
            metadata={"source": "test1"}
        ),
        Document(
            page_content="Test document two",
            metadata={"source": "test2"}
        )
    ]
    
    # Create and save store
    print("Creating initial store...")
    embeddings = get_embeddings_model()
    store = FAISSVectorStore.create(embeddings, docs)
    store.save()
    
    # Test initial search
    results = store.similarity_search("test", k=1)
    print(f"Initial search results: {len(results)}")
    
    # Create new store instance (should load existing data)
    print("\nLoading store from disk...")
    new_store = FAISSVectorStore(embeddings)
    
    # Test search with loaded store
    results = new_store.similarity_search("test", k=1)
    print(f"Loaded store search results: {len(results)}")
    
    # Add new document to loaded store
    print("\nAdding new document to loaded store...")
    new_store.add_documents([
        Document(
            page_content="Test document three",
            metadata={"source": "test3"}
        )
    ])
    
    # Verify document was added
    results = new_store.similarity_search("three", k=1)
    print(f"Search results after adding document: {len(results)}")
    
    print("\nPersistence test complete!")

if __name__ == "__main__":
    test_store_persistence()