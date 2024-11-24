from fastapi import APIRouter, Depends, HTTPException
from app.api.routers.chat.requests import ChatRequest
from app.api.routers.chat.responses import ChatResponse
from app.api.routers.chat.dependencies import get_chat_manager
from app.src.llm.chat_manager import ChatManager

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    try:
        response = await chat_manager.generate_response(request.messages)
        return ChatResponse(
            response=response.content,
            sources=response.sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))