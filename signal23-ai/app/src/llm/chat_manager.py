from typing import List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableSequence
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI

from app.src.llm.model_config import get_llm_model
from app.src.llm.prompt_templates import get_system_prompt
from app.src.rag.retriever import get_relevant_context
from app.api.routers.chat.requests import ChatMessage
from app.api.routers.chat.responses import ChatResponse, Source

class ChatManager:
    """
    Manages chat interactions with the LLM, including context retrieval and response generation.
    
    This class orchestrates the interaction between the API layer and the underlying LLM,
    handling prompt construction, context retrieval, and response formatting. It's designed
    to work within a Docker container and can switch between different LLM providers.

    Attributes:
        llm: The language model instance (either ChatOllama or ChatOpenAI)
        chain: The LangChain processing chain for handling requests
    """

    def __init__(self):
        """
        Initializes the ChatManager with the appropriate LLM model and processing chain.
        The model selection is determined by environment variables in the Docker configuration.
        """
        self.llm = get_llm_model()
        self.chain = self._create_chain()

    def _create_chain(self) -> RunnableSequence:
            """
            Creates the LangChain processing chain for handling chat requests.
            """
            prompt = ChatPromptTemplate.from_messages([
                ("system", get_system_prompt()),
                ("user", "{question}"),
                ("context", "{context}")
            ])

            chain = (
                {
                    "question": RunnablePassthrough(),
                    "context": get_relevant_context  # Now using the helper function directly
                }
                | prompt
                | self.llm
                | StrOutputParser()
            )
            
            return chain

    async def generate_response(self, messages: List[ChatMessage]) -> ChatResponse:
        """
        Generates a response to a chat message using the LLM and context retrieval.

        Args:
            messages: List of chat messages, including conversation history.
                     Expected to be in chronological order with the latest message last.

        Returns:
            ChatResponse: Contains the AI's response and any relevant source documents.
                         Sources may be None if no relevant context is found.

        Raises:
            Exception: If there's an error in context retrieval or LLM processing.
                      These are caught by the FastAPI error handler.
        """
        user_message = messages[-1].content
        response = await self.chain.ainvoke(user_message)
        sources = self._get_sources(user_message)
        
        return ChatResponse(
            response=response,
            sources=sources
        )
    
    def _get_sources(self, question: str) -> Optional[List[Source]]:
        """
        Retrieves source documents relevant to the user's question.
        
        This is a placeholder method that should be implemented based on your
        specific RAG setup. It would typically interact with a vector store
        to find relevant documentation.

        Args:
            question: The user's question to find sources for

        Returns:
            Optional[List[Source]]: List of relevant sources if found, None otherwise
        """
        return None