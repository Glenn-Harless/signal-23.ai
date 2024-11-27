import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

import os
from dotenv import load_dotenv
from app.src.data.notion_loader import NotionLoader
from app.src.data.data_processor import DataProcessor
from app.src.data.embeddings import get_embeddings_model
from app.src.rag.faiss_store import FAISSVectorStore
from langchain_core.documents import Document

def load_notion_to_faiss():
    """Load Notion content into FAISS vector store"""
    # Load environment variables
    load_dotenv()
    
    # Initialize components
    notion = NotionLoader(token=os.getenv("NOTION_API_KEY"))
    embeddings_model = get_embeddings_model()
    processor = DataProcessor(
        notion_loader=notion,
        embeddings_generator=embeddings_model,
        chunk_size=500,
        chunk_overlap=50
    )
    
    try:
        # Load and process documents from Notion
        database_id = os.getenv("NOTION_DATABASE_ID")
        if not database_id:
            raise ValueError("NOTION_DATABASE_ID not set in environment variables")
            
        print(f"Using Notion database ID: {database_id}")
        print("Loading documents from Notion...")
        
        processed_chunks = processor.process_database(database_id)
        print(f"Received {len(processed_chunks)} chunks from processor")
        
        if not processed_chunks:
            print("Warning: No chunks were processed from Notion database")
            return
            
        print(f"Converting {len(processed_chunks)} chunks to documents...")
        documents = [
            Document(
                page_content=chunk.text,
                metadata={
                    "source": chunk.source_url,
                    "title": chunk.metadata.title,  # Direct attribute access
                    "page_id": chunk.source_page,
                    "chunk_index": chunk.metadata.chunk_index,
                    "last_edited": chunk.metadata.last_edited
                }
            )
            for chunk in processed_chunks
        ]
        
        if not documents:
            print("Warning: No documents created from chunks")
            return
            
        print(f"Created {len(documents)} documents")
        print("Adding documents to FAISS...")
        
        # Create store with documents
        vector_store = FAISSVectorStore.create(embeddings_model, documents)
        
        print("Saving FAISS index...")
        vector_store.save()
        
        print("Successfully loaded Notion content into FAISS store!")
        return vector_store
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    load_notion_to_faiss()