from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from playwright.async_api import async_playwright
import base64
import os
import uuid
from datetime import datetime
import logging
import traceback
import re
import asyncio

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

os.makedirs("tmp", exist_ok=True)
os.makedirs("tmp/logos", exist_ok=True)
logger.info("Директории созданы: tmp/, tmp/logos/")

STYLE_TEMPLATES = {
    'minimal': {
        'bg_gradient': 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
        'text_color': '#1e293b',
        'accent_color': '#3b82f6',  # Синий
        'border_radius': '16px',
        'shadow': '0 10px 40px rgba(59, 130, 246, 0.1)',
        'font_family': "'Inter', sans-serif"
    },
    'corporate': {
        'bg_gradient': 'linear-gradient(135deg, #f9fafb 0%, #e5e7eb 100%)',
        'text_color': '#374151',
        'accent_color': '#1e3a8a',  # Тёмно-синий (корпоративный)
        'border_radius': '8px',
        'shadow': '0 4px 6px rgba(30, 58, 138, 0.1)',
        'font_family': "'Roboto', Arial, sans-serif"
    },
    'creative': {
        'bg_gradient': 'linear-gradient(135deg, #f0f9ff 0%, #fef3c7 100%)',
        'text_color': '#4b5563',
        'accent_color': '#8b5cf6',  # Фиолетовый
        'border_radius': '24px',
        'shadow': '0 20px 60px rgba(139, 92, 246, 0.2)',
        'font_family': "'Poppins', sans-serif"
    },
    'luxury': {
        'bg_gradient': 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
        'text_color': '#854d0e',
        'accent_color': '#b45309',  # Золотой/оранжевый (люкс)
        'border_radius': '12px',
        'shadow': '0 15px 50px rgba(180, 83, 9, 0.2)',
        'font_family': "'Georgia', serif"
    },
    'modern': {  # НОВЫЙ СТИЛЬ
        'bg_gradient': 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
        'text_color': '#1e293b',
        'accent_color': '#0ea5e9',  # Голубой/бирюзовый
        'border_radius': '20px',
        'shadow': '0 10px 40px rgba(14, 165, 233, 0.15)',
        'font_family': "'Inter', sans-serif"
    },
    'elegant': {  # НОВЫЙ СТИЛЬ
        'bg_gradient': 'linear-gradient(135deg, #ffffff 0%, #f3f4f6 100%)',
        'text_color': '#334155',
        'accent_color': '#7e22ce',  # Пурпурный
        'border_radius': '16px',
        'shadow': '0 10px 40px rgba(126, 34, 206, 0.12)',
        'font_family': "'Playfair Display', Georgia, serif"
    }
}

def clean_ai_text(text: str) -> str:
    """Очищает текст от маркдаун форматирования и эмодзи"""
    text = re.sub(r'[^\w\s\.,!?;:()\-\n]', '', text)
    text = re.sub(r'[\*\_\#\`]+', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    text = '\n'.join([line.strip() for line in text.split('\n')])
    return text.strip()

def escape_html(text: str) -> str:
    """Экранирует спецсимволы HTML для безопасности"""
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))

@router.post("/generate")
async def generate_pdf(
    logo: UploadFile = File(...),
    text: str = Form(""),
    style: str = Form("minimal")
):
    unique_id = str(uuid.uuid4())
    logo_path = None
    pdf_path = f"tmp/{unique_id}.pdf"
    
    try:
        logger.info(f"Начало генерации PDF. ID: {unique_id}, Стиль: {style}")
        
        # Читаем логотип
        logo_content = await logo.read()
        logger.info(f"Логотип прочитан. Размер: {len(logo_content)} байт")
        
        # Сохраняем файл
        logo_filename = f"{unique_id}_{logo.filename}"
        logo_path = os.path.join("tmp", "logos", logo_filename)
        with open(logo_path, "wb") as f:
            f.write(logo_content)
        logger.info(f"Логотип сохранен: {logo_path}")
        
        # Конвертируем в base64
        logo_base64 = base64.b64encode(logo_content).decode('utf-8')
        logger.info(f"Логотип конвертирован в base64. Длина: {len(logo_base64)} символов")
        
        # Получаем параметры стиля
        style_params = STYLE_TEMPLATES.get(style, STYLE_TEMPLATES['minimal'])
        logger.info(f"Используемый стиль: {style}")
        
        # Очищаем и экранируем текст
        clean_text = clean_ai_text(text) if text else "Ваш профессиональный текст будет здесь."
        safe_text = escape_html(clean_text)
        logger.debug(f"Очищенный текст для PDF: {safe_text[:100]}...")
        
        # HTML шаблон
        html_template = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: {style_params['font_family']}; 
                    margin: 40px;
                }}
                .header {{
                    background: {style_params['accent_color']};
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: {style_params['border_radius']} {style_params['border_radius']} 0 0;
                }}
                .logo {{
                    max-width: 200px;
                    max-height: 100px;
                    margin-bottom: 20px;
                }}
                .content {{
                    padding: 40px;
                    color: {style_params['text_color']};
                    line-height: 1.6;
                }}
                .footer {{
                    background: {style_params['accent_color']};
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 0 0 {style_params['border_radius']} {style_params['border_radius']};
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <img src="data:image/png;base64,{logo_base64}" class="logo" alt="Logo">
                <h1>Ваша Презентация</h1>
            </div>
            <div class="content">
                <p>{safe_text}</p>
            </div>
            <div class="footer">
                <p>PDF Generator Pro • {datetime.now().strftime('%d.%m.%Y')}</p>
            </div>
        </body>
        </html>
        """
        
        logger.info("HTML шаблон сформирован")
        
        # Сохраняем для отладки
        debug_html_path = f"tmp/debug_{unique_id}.html"
        with open(debug_html_path, "w", encoding="utf-8") as f:
            f.write(html_template)
        logger.info(f"Отладочный HTML сохранен: {debug_html_path}")
        
        # Генерируем PDF через Async Playwright
        logger.info("Запуск Async Playwright для генерации PDF...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
            logger.info("Браузер запущен")
            
            page = await browser.new_page()
            logger.info("Страница создана")
            
            await page.set_viewport_size({"width": 1240, "height": 1754})
            await page.set_content(html_template, wait_until="networkidle", timeout=30000)
            logger.info("Контент загружен")
            
            await page.pdf(path=pdf_path, format='A4', print_background=True)
            logger.info(f"PDF сохранен: {pdf_path}")
            
            await browser.close()
            logger.info("Браузер закрыт")
        
        # Проверяем файл
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="PDF файл не был создан")
        
        file_size = os.path.getsize(pdf_path)
        logger.info(f"Размер сгенерированного PDF: {file_size} байт")
        logger.info("=== PDF УСПЕШНО СГЕНЕРИРОВАН ===")
        
        return FileResponse(
            pdf_path,
            media_type='application/pdf',
            filename=f'offer_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    
    except Exception as e:
        logger.error(f"Ошибка при генерации PDF: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Очистка временных файлов
        try:
            if logo_path and os.path.exists(logo_path):
                os.remove(logo_path)
                logger.info(f"Временный файл логотипа удален: {logo_path}")
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                logger.info(f"Временный PDF файл удален: {pdf_path}")
        except:
            pass
        
        raise HTTPException(status_code=500, detail=f"Ошибка генерации PDF: {str(e)}")