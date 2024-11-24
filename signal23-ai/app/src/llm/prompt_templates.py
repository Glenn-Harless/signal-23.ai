def get_system_prompt() -> str:
    """
    Returns the system prompt that defines the AI assistant's behavior.
    
    This prompt is crucial for maintaining consistent personality and
    response quality. It's injected into every conversation with the LLM.

    The prompt template includes a {context} placeholder that will be
    filled with relevant documentation during execution.

    Returns:
        str: The system prompt template with placeholders
    """
    return """You are an AI assistant for the band Signal23. You should maintain their 
    personality and tone while providing accurate information based on their documentation. 
    Use the provided context to inform your responses, but maintain a natural conversational flow.
    
    If you don't have enough context to answer a question accurately, acknowledge this
    and suggest that the user ask about something else or rephrase their question.
    
    Current context: {context}
    """