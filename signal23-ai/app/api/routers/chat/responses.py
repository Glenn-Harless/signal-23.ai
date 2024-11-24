from pydantic import BaseModel, Field
from typing import List, Optional

class Source(BaseModel):
    title: str = Field(..., description="Title of the source document")
    content: str = Field(..., description="Relevant content from source")
    confidence: float = Field(..., description="Relevance score")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI generated response")
    sources: Optional[List[Source]] = Field(None, description="Source documents used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "The band was formed in...",
                "sources": [
                    {
                        "title": "Band History",
                        "content": "Excerpt from source...",
                        "confidence": 0.92
                    }
                ]
            }
        }