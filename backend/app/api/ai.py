from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os
import json

router = APIRouter()

# Берем из Railway или используем твой ключ напрямую для верности
RAW_KEY = "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"
API_KEY = os.getenv("OPENROUTER_API_KEY", RAW_KEY).strip()

class AIRequest(BaseModel):
    prompt: str
    context: str = ""

@router.post("/generate-text")
async def generate_ai_text(request: AIRequest):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "model": "google/gemini-2.0-flash-exp:free", # САМАЯ СТАБИЛЬНАЯ БЕСПЛАТНАЯ
                "messages": [
                    {"role": "system", "content": "Ты маркетолог. Пиши кратко, без эмодзи и оформления."},
                    {"role": "user", "content": f"Тема: {request.context}\nЗадание: {request.prompt}"}
                ]
            }
            
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "HTTP-Referer": "https://vercel.app", # Нужен для бесплатных моделей
                    "Content-Type": "application/json"
                },
                json=payload
            )

            res_data = response.json()

            if response.status_code != 200:
                # Если OpenRouter ругается, мы вытащим причину
                error_msg = res_data.get('error', {}).get('message', 'Unknown error')
                raise Exception(f"OpenRouter Error {response.status_code}: {error_msg}")

            generated_text = res_data['choices'][0]['message']['content']
            return {"text": generated_text, "success": True}

    except Exception as e:
        print(f"Full Error: {str(e)}")
        # Выводим конкретную ошибку на фронтенд
        raise HTTPException(status_code=500, detail=str(e))
