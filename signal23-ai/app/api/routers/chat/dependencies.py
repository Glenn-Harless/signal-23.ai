from fastapi import Depends, HTTPException
from typing import Optional
from src.llm.chat_manager import ChatManager

async def get_chat_manager() -> ChatManager:
    try:
        return ChatManager()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to initialize chat manager")
