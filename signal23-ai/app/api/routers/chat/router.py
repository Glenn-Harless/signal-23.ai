from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.api.routers.chat.requests import ChatRequest
from app.api.routers.chat.responses import ChatResponse
from app.api.routers.chat.dependencies import get_chat_manager
from app.src.llm.chat_manager import ChatManager
import asyncio

router = APIRouter(prefix="/chat", tags=["chat"])

import logging

logger = logging.getLogger(__name__)

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    try:
        logger.info("Starting chat request processing")
        logger.info(f"Received messages: {request.messages}")
        
        logger.info("Initializing response generation")
        response = await asyncio.wait_for(
            chat_manager.generate_response(request.messages),
            timeout=120.0
        )
        
        logger.info("Response generated successfully")
        logger.info(f"Response content: {response}")
        
        return ChatResponse(
            response=response.response,
            sources=response.sources
        )
    except asyncio.TimeoutError:
        logger.error("Request timed out")
        raise HTTPException(status_code=504, detail="Request timed out")
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))