#!/usr/bin/env python3
"""
Telegram бот с интеграцией Google Gemini AI
Автор: AI Assistant
Дата: 2025
"""

import asyncio
import logging
import sys
from bot import TelegramBot

def main():
    """Основная функция для запуска бота"""
    
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🚀 Инициализация Telegram бота с Gemini AI...")
        
        # Создаем и запускаем бота
        bot = TelegramBot()
        
        logger.info("✅ Бот успешно запущен и готов к работе!")
        logger.info("📱 Начинаем прослушивание сообщений...")
        
        # Запускаем бота
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки (Ctrl+C)")
        logger.info("👋 Завершение работы бота...")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
        
    finally:
        logger.info("🔚 Бот остановлен")

if __name__ == "__main__":
    main()
