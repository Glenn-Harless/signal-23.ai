from pathlib import Path
import sys
import logging
from typing import List
import asyncio

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from langchain_core.documents import Document
from app.src.llm.chat_manager import ChatManager
from app.api.routers.chat.requests import ChatMessage
from app.src.rag.faiss_store import FAISSVectorStore
from app.src.data.embeddings import get_embeddings_model

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_test_data() -> FAISSVectorStore:
    """Initialize test documents in FAISS store"""
    documents = [
        Document(
            page_content="""Signal23 is an experimental electronic music project exploring themes 
            of forgotten transmissions and digital archaeology. Their sound combines elements of 
            ambient, glitch, and industrial music.""",
            metadata={"title": "Band Overview", "source": "test_doc_1"}
        ),
        Document(
            page_content="""The latest Signal23 release features deep atmospheric soundscapes 
            built from discovered number station recordings and corrupted data streams. Each track 
            represents a different recovered transmission.""",
            metadata={"title": "Latest Release", "source": "test_doc_2"}
        ),
        Document(
            page_content="""The band's live performances take place in abandoned technical facilities, 
            where they integrate the building's own electrical signals and ambient sounds into 
            their music.""",
            metadata={"title": "Live Performances", "source": "test_doc_3"}
        )
    ]
    
    embeddings = get_embeddings_model()
    store = FAISSVectorStore.create(embeddings, documents)
    store.save()
    return store

async def test_conversation():
    """Test the chat manager with various queries"""
    logger.info("Initializing test data...")
    setup_test_data()
    
    chat_manager = ChatManager()
    
    test_messages = [
        ChatMessage(
            role="user",
            content="Tell me about Signal23. What kind of music do they make?"
        ),
        ChatMessage(
            role="user",
            content="What can you tell me about their latest release?"
        ),
        ChatMessage(
            role="user",
            content="How do they perform live?"
        ),
        ChatMessage(
            role="user",
            content="What influences their sound?"
        )
    ]
    
    for message in test_messages:
        print("\n" + "="*50)
        print(f"\nUser: {message.content}")
        
        try:
            response = await chat_manager.generate_response([message])
            print(f"\nAI: {response.response}")
            
            if response.sources:
                print("\nSources used:")
                for source in response.sources:
                    print(f"- {source.title} (Confidence: {source.confidence:.2f})")
                    
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise

async def test_conversation_flow():
    """Test a more natural conversation flow with context"""
    chat_manager = ChatManager()
    
    conversation = [
        ChatMessage(role="user", content="Hi, I'm interested in learning about Signal23"),
        ChatMessage(role="user", content="That's fascinating! Where do they perform?"),
        ChatMessage(role="user", content="How do they use the facility sounds in their music?"),
        ChatMessage(role="user", content="Can you describe their musical style in more detail?")
    ]
    
    history = []
    
    for message in conversation:
        history.append(message)
        print("\n" + "="*50)
        print(f"\nUser: {message.content}")
        
        try:
            response = await chat_manager.generate_response(history)
            print(f"\nAI: {response.response}")
            history.append(ChatMessage(role="assistant", content=response.response))
            
        except Exception as e:
            logger.error(f"Error in conversation: {e}")
            raise

async def main():
    """Run all tests"""
    print("Testing individual queries...")
    await test_conversation()
    
    print("\nTesting conversation flow...")
    await test_conversation_flow()

if __name__ == "__main__":
    asyncio.run(main())