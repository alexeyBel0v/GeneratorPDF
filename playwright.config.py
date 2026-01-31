# playwright.config.py
from playwright.sync_api import sync_playwright

# Проверка установки браузера
with sync_playwright() as p:
    try:
        browser = p.chromium.launch(headless=True)
        browser.close()
        print("✅ Playwright работает корректно")
    except Exception as e:
        print(f"❌ Ошибка Playwright: {e}")
        print("Установите браузер: playwright install chromium")