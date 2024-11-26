# app/test_ai.py
import asyncio
from app.src.llm.chat_manager import ChatManager
from app.api.routers.chat.requests import ChatMessage

async def test_conversation():
    chat_manager = ChatManager()
    
    # Test messages
    test_messages = [
        ChatMessage(
            role="user",
            content="Tell me about Signal23. What kind of music do you make?"
        ),
        ChatMessage(
            role="user",
            content="Can you explain the concept behind your latest work?"
        ),
        ChatMessage(
            role="user",
            content="What influences your sound?"
        )
    ]
    
    # Try each message
    for message in test_messages:
        print("\nUser:", message.content)
        response = await chat_manager.generate_response([message])
        print("\nAI:", response.response)
        print("\n" + "="*50)

if __name__ == "__main__":
    asyncio.run(test_conversation())