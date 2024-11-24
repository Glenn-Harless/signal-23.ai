from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers.chat.router import router as chat_router

app = FastAPI(title="Signal23 AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/v1")

# Basic health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
