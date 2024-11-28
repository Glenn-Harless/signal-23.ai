from typing import List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableSequence
from app.src.llm.model_config import get_llm_model
from app.src.llm.prompt_templates import get_system_prompt
from app.src.rag.retriever import get_relevant_context
from app.api.routers.chat.requests import ChatMessage
from app.api.routers.chat.responses import ChatResponse, Source
from app.src.persona.signal23_personality import Signal23AI, AIAttributes
import logging

logger = logging.getLogger(__name__)

class ChatManager:
    def __init__(self):
        self.llm = get_llm_model()
        self.signal23_ai = Signal23AI()
        self.chain = self._create_chain()

    def _create_chain(self) -> RunnableSequence:
        prompt = ChatPromptTemplate.from_messages([
            ("system", get_system_prompt() + "\n" + self.signal23_ai.get_system_prompt_additions()),
            ("user", """Here is some relevant context to help answer the question:
            {context}
            
            Question: {question}
            """)
        ])

        chain = (
            {
                "context": get_relevant_context,
                "question": lambda x: x
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return chain

    def _determine_response_type(self, message: str) -> str:
        """Determine the appropriate transmission type based on message content"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["music", "sound", "track", "album"]):
            return "music_discussion"
        elif any(word in message_lower for word in ["history", "story", "background", "lore"]):
            return "lore"
        elif any(word in message_lower for word in ["how", "what", "explain", "technical"]):
            return "technical"
        elif "error" in message_lower or "wrong" in message_lower:
            return "error"
        else:
            return "greeting"

    def _format_ai_response(self, message: str, user_query: str) -> str:
        """Format the AI response with Signal23 personality"""
        # Determine response type
        context_type = self._determine_response_type(user_query)
        
        # Get appropriate transmission style
        style = self.signal23_ai.get_transmission_style(
            context_type=context_type,
            topic=user_query[:30] + "..." if len(user_query) > 30 else user_query
        )
        
        # Format the message with template
        formatted_message = style["template"].format(
            message=message,
            id=style["id"],
            topic=style["topic"]
        )
        
        # Add glitch effects and formatting
        return self.signal23_ai.format_transmission(
            formatted_message,
            AIAttributes(**style["attributes"])
        )

    async def generate_response(self, messages: List[ChatMessage]) -> ChatResponse:
        logger.info("Starting response generation in ChatManager")
        try:
            user_message = messages[-1].content
            logger.info(f"Processing user message: {user_message}")
            
            logger.info("Invoking LLM chain")
            raw_response = await self.chain.ainvoke(user_message)
            logger.info(f"Raw response received: {raw_response}")
            
            logger.info("Formatting response with Signal23 personality")
            formatted_response = self._format_ai_response(raw_response, user_message)
            
            sources = self._get_sources(user_message)
            logger.info("Response generation complete")
            
            return ChatResponse(
                response=formatted_response,
                sources=sources
            )
        except Exception as e:
            logger.error(f"Error in generate_response: {str(e)}")
            raise
    
    def _get_sources(self, question: str) -> Optional[List[Source]]:
        return None