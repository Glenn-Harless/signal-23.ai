#!/bin/bash

# Prompt for project name (default to signal23-ai if no input)
read -p "Enter project name (default: signal23-ai): " PROJECT_NAME
PROJECT_NAME=${PROJECT_NAME:-signal23-ai}

# Create main project directory
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME

# Create directory structure
mkdir -p app/{src/{data,rag,llm,persona},api/routers,tests,config}

# Create Python files with __init__.py
touch app/src/{data,rag,llm,persona}/__init__.py
touch app/api/{__init__.py,main.py}
touch app/api/routers/{__init__.py,chat.py}
touch app/tests/__init__.py
touch app/src/data/{notion_loader.py,data_processor.py,embeddings.py}
touch app/src/rag/{retriever.py,context_builder.py}
touch app/src/llm/{prompt_templates.py,chat_manager.py}
touch app/src/persona/band_personality.py

# Create Docker and config files
touch app/Dockerfile
touch docker-compose.yml
touch .env
touch .dockerignore
touch app/requirements.txt
touch app/config/config.yaml
touch README.md

# Create basic .env file
cat << 'END' > .env
# API Keys
OPENAI_API_KEY=your-api-key-here
NOTION_TOKEN=your-notion-token

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/db_name

# Service Ports
API_PORT=8000
END

# Create basic .dockerignore
cat << 'END' > .dockerignore
__pycache__
*.pyc
.env
.git
.gitignore
README.md
tests/
.pytest_cache
.coverage
END

# Create a basic README
cat << END > README.md
# $PROJECT_NAME

AI Assistant trained on custom documentation.

## Setup

1. Configure environment variables in \`.env\`
2. Run \`docker-compose up --build\`

## Development

Project structure:
\`\`\`
app/
├── src/         # Core logic
├── api/         # FastAPI endpoints
├── tests/       # Test suite
└── config/      # Configuration files
\`\`\`
END

echo "Project $PROJECT_NAME created successfully!"
echo "Next steps:"
echo "1. Review and update .env with your credentials"
echo "2. Choose and set up your vector database"
echo "3. Configure your LLM (Ollama/OpenAI)"
echo "4. Run 'docker-compose up --build' to start development"