# app/startup.py
import httpx
import asyncio
import logging
from typing import Optional
import os
import time

logger = logging.getLogger(__name__)

async def wait_for_ollama(base_url: str, timeout: int = 300) -> bool:
    """Wait for Ollama to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url}/api/tags")
                if response.status_code == 200:
                    logger.info("Ollama is ready")
                    return True
        except Exception as e:
            logger.warning(f"Waiting for Ollama to be ready: {str(e)}")
        await asyncio.sleep(2)
    return False

async def pull_model(base_url: str, model_name: str) -> bool:
    """Pull the specified model"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/api/pull",
                json={"name": model_name}
            )
            if response.status_code == 200:
                logger.info(f"Successfully pulled model: {model_name}")
                return True
    except Exception as e:
        logger.error(f"Error pulling model: {str(e)}")
    return False

async def initialize_ollama():
    """Initialize Ollama and pull required model"""
    base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    model_name = os.getenv("OLLAMA_MODEL_NAME", "mistral")
    
    logger.info("Waiting for Ollama to be ready...")
    if not await wait_for_ollama(base_url):
        raise RuntimeError("Ollama failed to start")
        
    logger.info(f"Pulling model: {model_name}")
    if not await pull_model(base_url, model_name):
        raise RuntimeError(f"Failed to pull model: {model_name}")
        
    logger.info("Ollama initialization complete")