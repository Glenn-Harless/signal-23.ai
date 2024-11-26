# app/src/data/embedding_models.py
from typing import Dict, List, Optional, Type
from pydantic import BaseModel
from abc import ABC, abstractmethod
from langchain.embeddings import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
import logging
import os

logger = logging.getLogger(__name__)

class EmbeddingModelConfig(BaseModel):
    """Configuration for embedding models"""
    name: str
    dimension: int
    max_tokens: int
    batch_size: int
    model_type: str
    api_config: Dict[str, any]

class EmbeddingModelBase(ABC):
    """Base class for embedding model implementations"""
    
    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        pass
    
    @abstractmethod
    async def generate_query_embedding(self, text: str) -> List[float]:
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        pass

class OllamaEmbeddingModel(EmbeddingModelBase):
    """Ollama embedding model implementation"""
    
    def __init__(self, config: EmbeddingModelConfig):
        self.config = config
        self.model = OllamaEmbeddings(
            base_url=config.api_config.get("base_url", "http://ollama:11434"),
            model=config.name
        )
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        return await self.model.aembed_documents(texts)
    
    async def generate_query_embedding(self, text: str) -> List[float]:
        return await self.model.aembed_query(text)
    
    @property
    def dimension(self) -> int:
        return self.config.dimension

class OpenAIEmbeddingModel(EmbeddingModelBase):
    """OpenAI embedding model implementation"""
    
    def __init__(self, config: EmbeddingModelConfig):
        self.config = config
        self.model = OpenAIEmbeddings(
            model=config.name,
            openai_api_key=config.api_config.get("api_key")
        )
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        return await self.model.aembed_documents(texts)
    
    async def generate_query_embedding(self, text: str) -> List[float]:
        return await self.model.aembed_query(text)
    
    @property
    def dimension(self) -> int:
        return self.config.dimension

class EmbeddingModelFactory:
    """Factory for creating embedding model instances"""
    
    _models: Dict[str, Type[EmbeddingModelBase]] = {
        "ollama": OllamaEmbeddingModel,
        "openai": OpenAIEmbeddingModel
    }
    
    _configs: Dict[str, EmbeddingModelConfig] = {
        "mistral": EmbeddingModelConfig(
            name="mistral",
            dimension=384,
            max_tokens=8192,
            batch_size=10,
            model_type="ollama",
            api_config={"base_url": "http://ollama:11434"}
        ),
        "text-embedding-ada-002": EmbeddingModelConfig(
            name="text-embedding-ada-002",
            dimension=1536,
            max_tokens=8191,
            batch_size=100,
            model_type="openai",
            api_config={"api_key": os.getenv("OPENAI_API_KEY")}
        )
    }
    
    @classmethod
    def create_model(cls, model_name: str) -> EmbeddingModelBase:
        """Create embedding model instance"""
        config = cls._configs.get(model_name)
        if not config:
            raise ValueError(f"Unknown model: {model_name}")
            
        model_class = cls._models.get(config.model_type)
        if not model_class:
            raise ValueError(f"Unknown model type: {config.model_type}")
            
        return model_class(config)
    
    @classmethod
    def register_model(
        cls,
        model_name: str,
        config: EmbeddingModelConfig,
        model_class: Type[EmbeddingModelBase]
    ):
        """Register new embedding model type"""
        cls._configs[model_name] = config
        cls._models[config.model_type] = model_class

# Singleton instance for model management
_model_instance: Optional[EmbeddingModelBase] = None

def get_embedding_model(
    model_name: Optional[str] = None,
    force_new: bool = False
) -> EmbeddingModelBase:
    """Get or create embedding model instance"""
    global _model_instance
    
    if _model_instance is None or force_new:
        model_name = model_name or os.getenv("EMBEDDING_MODEL", "mistral")
        _model_instance = EmbeddingModelFactory.create_model(model_name)
    
    return _model_instance