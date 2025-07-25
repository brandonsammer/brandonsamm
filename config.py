import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Конфигурация бота
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Проверяем наличие обязательных переменных
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY не найден в переменных окружения")

# Настройки для логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
