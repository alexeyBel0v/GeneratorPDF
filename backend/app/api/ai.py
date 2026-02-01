from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os
from typing import Optional

router = APIRouter()

# Приоритет: 1. Переменная в Railway, 2. Твой новый ключ
API_KEY = os.getenv("OPENROUTER_API_KEY", "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")

class AIRequest(BaseModel):
    prompt: str
    context: Optional[str] = ""

class AIResponse(BaseModel):
    text: str
    success: bool

@router.post("/generate-text", response_model=AIResponse)
async def generate_ai_text(request: AIRequest):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://vercel.app",
                    "X-Title": "PDFGen"
                },
                json={
                    "model": "google/gemini-2.0-flash-exp:free",
                    "messages": [
                        {"role": "system", "content": "Ты маркетолог. Пиши только чистый текст без разметки."},
                        {"role": "user", "content": f"{request.context}\n\n{request.prompt}"}
                    ]
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenRouter Error: {response.text}")
            
            result = response.json()
            return AIResponse(text=result['choices'][0]['message']['content'], success=True)
    except Exception as e:
        # Это выведет ошибку в логи Railway
        print(f"CRITICAL AI ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
