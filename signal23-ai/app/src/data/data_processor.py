from typing import List, Dict
import logging
from pydantic import BaseModel
from app.src.data.notion_loader import NotionLoader, NotionPage
from app.src.data.embeddings import EmbeddingsGenerator

logger = logging.getLogger(__name__)

class ProcessedChunk(BaseModel):
    """Represents a processed text chunk with its metadata"""
    text: str
    embedding: List[float]
    metadata: Dict[str, any]
    source_page: str
    source_url: str

class DataProcessor:
    """Processes Notion content into chunks with embeddings"""
    def __init__(
        self, 
        notion_loader: NotionLoader,
        embeddings_generator: EmbeddingsGenerator,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        self.notion_loader = notion_loader
        self.embeddings_generator = embeddings_generator
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    async def process_database(self, database_id: str) -> List[ProcessedChunk]:
        """Process all pages in a Notion database"""
        # Load pages from Notion
        pages = await self.notion_loader.load_database(database_id)
        
        # Process each page
        all_chunks = []
        for page in pages:
            chunks = self._chunk_text(page)
            embeddings = await self.embeddings_generator.generate_embeddings(
                [chunk.text for chunk in chunks]
            )
            
            # Combine chunks with their embeddings
            for chunk, embedding in zip(chunks, embeddings):
                chunk.embedding = embedding
                all_chunks.append(chunk)
        
        logger.info(f"Processed {len(all_chunks)} chunks from {len(pages)} pages")
        return all_chunks

    def _chunk_text(self, page: NotionPage) -> List[ProcessedChunk]:
        """Split page content into chunks"""
        text = page.content
        chunks = []
        start = 0
        
        while start < len(text):
            # Find chunk end
            end = start + self.chunk_size
            if end > len(text):
                end = len(text)
            else:
                # Try to find natural break point
                next_newline = text[end:end+100].find('\n')
                if next_newline != -1:
                    end += next_newline
            
            # Create chunk with metadata
            chunk = ProcessedChunk(
                text=text[start:end].strip(),
                embedding=[],  # Will be filled later
                metadata={
                    'title': page.title,
                    'chunk_index': len(chunks),
                    **page.metadata
                },
                source_page=page.id,
                source_url=page.url
            )
            chunks.append(chunk)
            
            # Move start position for next chunk
            start = end - self.chunk_overlap
        
        return chunks