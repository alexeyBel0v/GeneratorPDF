import asyncio
import sys
import os

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as pdf_router
from app.api.ai import router as ai_router
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PDF Generator Pro", version="1.0.0")

# ИЗМЕНЕНО: Разрешаем запросы со всех доменов (для работы Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pdf_router)
app.include_router(ai_router, prefix="/ai")

@app.get("/")
async def root():
    return {"message": "API is running", "status": "ok"}

if __name__ == "__main__":
    import uvicorn
    # ИЗМЕНЕНО: Берем порт из переменной окружения Railway
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
