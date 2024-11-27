from typing import Union
import os
from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

def get_llm_model() -> BaseChatModel:
    """
    Factory function to create and configure the appropriate LLM instance.
    
    This function reads environment variables (typically set in docker-compose.yml
    or .env) to determine which LLM provider to use and how to configure it.
    
    Environment Variables:
        LLM_PROVIDER: 'ollama' or 'openai'
        OLLAMA_MODEL_NAME: Name of the Ollama model (default: 'mistral')
        OLLAMA_BASE_URL: URL of the Ollama service (default: 'http://localhost:11434')
        OPENAI_API_KEY: Required if using OpenAI
        OPENAI_MODEL_NAME: OpenAI model to use (default: 'gpt-3.5-turbo')
        LLM_TEMPERATURE: Temperature setting for generation (default: 0.7)

    Returns:
        BaseChatModel: Configured LLM instance (either ChatOllama or ChatOpenAI)

    Raises:
        ValueError: If LLM_PROVIDER is not supported
        EnvironmentError: If required environment variables are missing
    """
    model_provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    
    if model_provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY must be set when using OpenAI")
            
        return ChatOpenAI(
            model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            api_key=api_key
        )
    elif model_provider == "ollama":
        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL_NAME", "mistral"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )
    else:
        raise ValueError(f"Unsupported model provider: {model_provider}")
