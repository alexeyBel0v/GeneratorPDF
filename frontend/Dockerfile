FROM mcr.microsoft.com/playwright/python:3.11-focal

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Устанавливаем браузер
RUN playwright install chromium

# Порт
ENV PORT=8000

# Запуск
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]