from typing import List, Dict, Optional, Any
import logging
import time
from pydantic import BaseModel, Field
from app.src.data.notion_loader import NotionLoader, NotionPage
from app.src.data.embeddings import EnhancedEmbeddingsGenerator

logger = logging.getLogger(__name__)

class NotionProperties(BaseModel):
    """Structure for Notion page properties"""
    Notes: Optional[str] = None
    category: Optional[str] = None
    Tags: Optional[List[str]] = Field(default_factory=list)
    Description: Optional[str] = None

class PageMetadata(BaseModel):
    """Metadata structure for a processed chunk"""
    title: str
    chunk_index: int
    last_edited: str
    properties: NotionProperties = Field(default_factory=NotionProperties)

class ProcessedChunk(BaseModel):
    """Represents a processed text chunk with its metadata"""
    text: str
    embedding: List[float] = Field(default_factory=list)
    metadata: PageMetadata
    source_page: str
    source_url: str

class DataProcessor:
    def __init__(
        self, 
        notion_loader: NotionLoader,
        embeddings_generator: EnhancedEmbeddingsGenerator,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        self.notion_loader = notion_loader
        self.embeddings_generator = embeddings_generator
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _clean_notion_properties(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and format Notion properties"""
        cleaned_props = {}
        try:
            for key, value in properties.items():
                if isinstance(value, (str, int, float, bool)):
                    cleaned_props[key] = value
                elif isinstance(value, list):
                    cleaned_props[key] = [str(item) for item in value]
                elif isinstance(value, dict):
                    cleaned_props[key] = str(value)
                else:
                    cleaned_props[key] = str(value)
        except Exception as e:
            print(f"Error cleaning properties: {e}")
            return {}
        return cleaned_props


    def _chunk_text(self, page: NotionPage) -> List[ProcessedChunk]:
        """Split page content into chunks"""
        text = page.content
        if not text.strip():
            print(f"Warning: Empty content for page {page.title}")
            return []
            
        chunks = []
        start = 0
        
        print(f"Starting chunking for page: {page.title}")
        print(f"Total text length: {len(text)}")
        chunk_start_time = time.time()
        
        # Safety check - if we're about to create too many chunks, something's wrong
        max_possible_chunks = len(text) // (self.chunk_size - self.chunk_overlap) + 1
        if max_possible_chunks > 100:  # Arbitrary reasonable limit
            print(f"Warning: Text would create too many chunks ({max_possible_chunks})")
            print(f"Text preview: {text[:200]}...")
            return []
        
        while start < len(text):
            # Calculate end position
            end = min(start + self.chunk_size, len(text))
            
            # If we're not at the end of the text, try to find a natural break point
            if end < len(text):
                # Look for natural break points
                for separator in ["\n\n", "\n", ". ", " "]:
                    next_break = text[end:min(end + 100, len(text))].find(separator)
                    if next_break != -1:
                        end += next_break + len(separator)
                        break
            
            # Get the chunk text
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                try:
                    # Clean and format the properties
                    cleaned_properties = self._clean_notion_properties(
                        page.metadata.properties if page.metadata else {}
                    )
                    
                    # Create properties model with defaults
                    notion_properties = NotionProperties()
                    for key, value in cleaned_properties.items():
                        if hasattr(notion_properties, key):
                            setattr(notion_properties, key, value)
                    
                    # Create metadata
                    metadata = PageMetadata(
                        title=page.title,
                        chunk_index=len(chunks),
                        last_edited=page.last_edited,
                        properties=notion_properties
                    )
                    
                    # Create chunk
                    chunk = ProcessedChunk(
                        text=chunk_text,
                        metadata=metadata,
                        source_page=page.id,
                        source_url=page.url
                    )
                    chunks.append(chunk)
                    print(f"Created chunk {len(chunks)} with length {len(chunk_text)}")
                except Exception as e:
                    print(f"Error creating chunk: {e}")
                    continue
            
            # Move start position for next chunk
            start = end - self.chunk_overlap
            
            # Safety break - if we're somehow stuck
            if start >= len(text) or len(chunks) > max_possible_chunks:
                break
        
        chunk_time = time.time() - chunk_start_time
        print(f"Chunking completed in {chunk_time:.2f} seconds")
        print(f"Created {len(chunks)} chunks from text of length {len(text)}")
        
        if chunks:
            print(f"First chunk preview: {chunks[0].text[:100]}...")
            
        return chunks
    def process_database(self, database_id: str) -> List[ProcessedChunk]:
        """Process all pages in a Notion database"""
        pages = self.notion_loader.load_database(database_id)
        print(f"\nProcessing {len(pages)} pages from Notion...")
        
        all_chunks = []
        for page in pages:
            try:
                print(f"\nProcessing page: {page.title}")
                print(f"Content length: {len(page.content)}")
                print(f"First 100 chars of content: {page.content[:100]}")
                
                # Time the chunking process
                chunk_start = time.time()
                chunks = self._chunk_text(page)
                chunk_time = time.time() - chunk_start
                print(f"Chunking took {chunk_time:.2f} seconds")
                
                if chunks:
                    print(f"Starting embedding generation for {len(chunks)} chunks...")
                    chunk_texts = [chunk.text for chunk in chunks]
                    
                    # Time the embedding process
                    embed_start = time.time()
                    embeddings = self.embeddings_generator.generate_embeddings(chunk_texts)
                    embed_time = time.time() - embed_start
                    print(f"Embedding generation took {embed_time:.2f} seconds")
                    
                    for chunk, embedding in zip(chunks, embeddings):
                        chunk.embedding = embedding
                        all_chunks.append(chunk)
                    print(f"Successfully processed {len(chunks)} chunks with embeddings")
                else:
                    print("No chunks created from this page")
                    
            except Exception as e:
                print(f"Error processing page {page.title}: {e}")
                print(f"Error type: {type(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                continue
        
        print(f"\nTotal chunks created: {len(all_chunks)}")
        return all_chunks