from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os
from typing import Optional

router = APIRouter()

# БЕРЕМ КЛЮЧ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ (Railway Variables)
# Если ключа в Railway нет, используем тот, что ты прислал как запасной
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

class AIRequest(BaseModel):
    prompt: str
    context: Optional[str] = ""

class AIResponse(BaseModel):
    text: str
    success: bool

@router.post("/generate-text", response_model=AIResponse)
async def generate_ai_text(request: AIRequest):
    try:
        system_prompt = """Ты профессиональный маркетолог. Создай чистый текст без эмодзи и Markdown-разметки (без **, ###, *)."""
        user_prompt = f"Тема: {request.context}\nЗадача: {request.prompt}"

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://vercel.com", # Обязательно для OpenRouter
                    "X-Title": "PDF Generator Pro"         # Обязательно для OpenRouter
                },
                json={
                    # ИСПОЛЬЗУЕМ БОЛЕЕ СТАБИЛЬНУЮ БЕСПЛАТНУЮ МОДЕЛЬ
                    "model": "google/gemini-2.0-flash-exp:free", 
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                }
            )
            
            if response.status_code != 200:
                # Печатаем ошибку в логи Railway, чтобы ты ее видел
                print(f"OpenRouter Error Response: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"OpenRouter API error: {response.text}"
                )
            
            result = response.json()
            if 'choices' not in result:
                raise Exception(f"Unexpected response from AI: {result}")
                
            generated_text = result['choices'][0]['message']['content']
            
            return AIResponse(
                text=generated_text,
                success=True
            )
    
    except Exception as e:
        print(f"AI generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
