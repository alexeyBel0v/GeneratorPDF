from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os
from typing import Optional

router = APIRouter()

# OpenRouter API Configuration
OPENROUTER_API_KEY = "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"
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
        # Формируем промпт БЕЗ эмодзи и маркдаун
        system_prompt = """Ты профессиональный маркетолог и копирайтер. 
Создай продающий, убедительный текст для презентации или предложения.
Текст должен быть структурированным, профессиональным и убедительным.
НЕ ИСПОЛЬЗУЙ эмодзи, звездочки (**), решетки (###) и другую разметку.
Пиши чистый текст без форматирования.
Длина текста: 150-200 слов."""

        user_prompt = f"""Контекст или тема: {request.context}

Задача: {request.prompt}

Создай профессиональный маркетинговый текст без эмодзи и форматирования."""

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "tngtech/deepseek-r1t2-chimera:free",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"OpenRouter API error: {response.text}"
                )
            
            result = response.json()
            generated_text = result['choices'][0]['message']['content']
            
            return AIResponse(
                text=generated_text,
                success=True
            )
    
    except Exception as e:
        print(f"AI generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка генерации текста: {str(e)}")