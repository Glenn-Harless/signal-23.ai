# signal23-ai

AI Assistant trained on custom documentation.

## Setup

1. Configure environment variables in `.env`
2. Run `docker-compose up --build`

## Development

Project structure:
```
app/
├── api/                      # FastAPI application layer
│   ├── main.py              # FastAPI app initialization, middleware, main config
│   └── routers/             # API route definitions
│
├── src/                     # Core application logic
│   ├── data/               # Data handling and processing
│   │   ├── notion_loader.py    # Notion API integration, document loading
│   │   ├── data_processor.py   # Text cleaning, chunking, preprocessing
│   │   └── embeddings.py       # Vector embedding generation and handling
│   │
│   ├── rag/                # Retrieval Augmented Generation logic
│   │   ├── retriever.py        # Vector search, relevant context retrieval
│   │   └── context_builder.py  # Assembling context for LLM prompts
│   │
│   ├── llm/                # Language Model integration
│   │   ├── chat_manager.py     # Chat history, conversation management
│   │   └── prompt_templates.py # System prompts, templating
│   │
│   └── persona/            # AI personality definition
│       └── band_personality.py # Persona traits, behavior rules
│
├── config/                  # Configuration management
│   └── config.yaml         # App settings, model params, system prompts
│
└── tests/                  # Test suite
    └── __init__.py         # Test configuration, fixtures
```
