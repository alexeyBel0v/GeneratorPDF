import asyncio
import sys

# ИСПРАВЛЕНИЕ ДЛЯ PYTHON 3.13 НА WINDOWS - ИСПОЛЬЗУЕМ Proactor
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as pdf_router
from app.api.ai import router as ai_router
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PDF Generator Pro",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pdf_router)
app.include_router(ai_router, prefix="/ai")

@app.get("/")
async def root():
    return {"message": "PDF Generator Pro API", "status": "ok"}

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Запуск сервера на http://127.0.0.1:8000 (Python {sys.version})")
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )