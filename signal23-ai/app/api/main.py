from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Basic health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Serve index.html at root
@app.get("/")
async def read_root():
    return FileResponse("app/static/index.html")
