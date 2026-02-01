from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os

router = APIRouter()

class AIRequest(BaseModel):
    prompt: str
    context: str = ""

@router.post("/generate-text")
async def generate_ai_text(request: AIRequest):
    # Берем ключ ТОЛЬКО из переменных Railway
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        raise HTTPException(status_code=500, detail="Ошибка: OPENROUTER_API_KEY не задан в Railway!")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key.strip()}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://vercel.app",
                },
                json={
                    "model": "google/gemini-2.0-flash-exp:free",
                    "messages": [{"role": "user", "content": f"{request.context}\n{request.prompt}"}]
                }
            )
            
            data = response.json()
            if response.status_code != 200:
                # Если OpenRouter вернет ошибку, мы увидим её текст
                error_msg = data.get('error', {}).get('message', 'Unknown Error')
                raise HTTPException(status_code=response.status_code, detail=error_msg)

            return {"text": data['choices'][0]['message']['content'], "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
