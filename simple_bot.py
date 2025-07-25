#!/usr/bin/env python3
"""
Простой Telegram бот с Gemini AI
Для запуска на локальном ПК
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai  # type: ignore

# Загружаем переменные из .env файла
load_dotenv()

# Получаем API ключи
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Проверяем наличие ключей
if not TELEGRAM_BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN не найден в .env файле!")
    print("Добавьте ваш токен бота в .env файл:")
    print("TELEGRAM_BOT_TOKEN=ваш_токен_здесь")
    exit(1)

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY не найден в .env файле!")
    print("Добавьте ваш API ключ Gemini в .env файл:")
    print("GEMINI_API_KEY=ваш_ключ_здесь")
    exit(1)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализируем Gemini клиент
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    if not update.message:
        return
    user_name = update.effective_user.first_name if update.effective_user else "Пользователь"
    welcome_message = (
        f"Привет, {user_name}! 👋\n\n"
        "Я AI-бот на базе Google Gemini. Просто напишите мне что-нибудь, и я отвечу!\n\n"
        "Команды:\n"
        "/start - Запуск бота\n"
        "/help - Помощь\n"
        "/analyze [текст] - Анализ текста"
    )
    await update.message.reply_text(welcome_message)
    logger.info(f"Пользователь {user_name} запустил бота")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /help"""
    if not update.message:
        return
    help_message = (
        "🤖 Доступные команды:\n\n"
        "/start - Запуск бота\n"
        "/help - Показать эту справку\n"
        "/analyze [текст] - Анализ текста\n\n"
        "Просто напишите мне любое сообщение, и я отвечу с помощью AI!"
    )
    await update.message.reply_text(help_message)

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /analyze"""
    if not update.message:
        return
    if not context.args:
        await update.message.reply_text(
            "Укажите текст для анализа.\nПример: /analyze Ваш текст"
        )
        return

    text_to_analyze = " ".join(context.args)
    analyzing_message = await update.message.reply_text("🔍 Анализирую...")
    
    try:
        prompt = f"Проанализируй этот текст и дай краткое резюме на русском:\n\n{text_to_analyze}"
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        analysis = response.text or "Не удалось проанализировать текст."
        await analyzing_message.edit_text(f"📊 Анализ:\n\n{analysis}")
        
    except Exception as e:
        logger.error(f"Ошибка анализа: {e}")
        await analyzing_message.edit_text("❌ Ошибка при анализе текста.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка обычных сообщений"""
    if not update.message or not update.message.text:
        return
        
    user_message = update.message.text
    user_name = update.effective_user.first_name if update.effective_user else "Пользователь"
    
    logger.info(f"Сообщение от {user_name}: {user_message[:50]}...")
    
    # Показываем, что печатаем
    if update.effective_chat:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Создаем промпт для Gemini
        prompt = (
            f"Ты дружелюбный AI-ассистент. Отвечай на русском языке. "
            f"Пользователя зовут {user_name}.\n\n"
            f"Вопрос: {user_message}"
        )
        
        # Получаем ответ от Gemini
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        ai_response = response.text or "Извините, не смог сгенерировать ответ."
        await update.message.reply_text(ai_response)
        
        logger.info(f"Ответ отправлен пользователю {user_name}")
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка. Попробуйте позже."
        )

def main():
    """Запуск бота"""
    print("🚀 Запуск Telegram бота...")
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("analyze", analyze_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Бот запущен и готов к работе!")
    print("📱 Ожидаю сообщений...")
    print("Для остановки нажмите Ctrl+C")
    
    try:
        # Запускаем бота
        application.run_polling()
    except KeyboardInterrupt:
        print("\n🛑 Остановка бота...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        print("👋 Бот остановлен")

if __name__ == "__main__":
    main()