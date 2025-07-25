import logging
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes
)
from gemini_client import GeminiClient
from config import TELEGRAM_BOT_TOKEN

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        """Инициализация Telegram бота"""
        self.gemini_client = GeminiClient()
        if not TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не найден")
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """Настройка обработчиков команд и сообщений"""
        # Обработчики команд
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("analyze", self.analyze_command))
        
        # Обработчик текстовых сообщений
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        if not update.message:
            return
        user_name = update.effective_user.first_name if update.effective_user else "Пользователь"
        welcome_message = (
            f"Привет, {user_name}! 👋\n\n"
            "Я AI-бот на базе Google Gemini. Я могу:\n"
            "• Отвечать на ваши вопросы\n"
            "• Помогать с различными задачами\n"
            "• Анализировать тексты\n\n"
            "Просто напишите мне что-нибудь, и я постараюсь помочь!\n\n"
            "Используйте /help для получения дополнительной информации."
        )
        await update.message.reply_text(welcome_message)
        logger.info(f"Пользователь {user_name} ({update.effective_user.id if update.effective_user else 'unknown'}) запустил бота")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /help"""
        if not update.message:
            return
        help_message = (
            "🤖 *Доступные команды:*\n\n"
            "/start - Запуск бота\n"
            "/help - Показать это сообщение\n"
            "/analyze - Анализ текста (используйте: /analyze ваш_текст)\n\n"
            "📝 *Как использовать:*\n"
            "Просто напишите мне любое сообщение, и я отвечу с помощью AI!\n\n"
            "Я могу помочь с:\n"
            "• Ответами на вопросы\n"
            "• Объяснениями сложных тем\n"
            "• Переводом текста\n"
            "• Написанием текстов\n"
            "• И многим другим!"
        )
        await update.message.reply_text(help_message, parse_mode='Markdown')

    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /analyze"""
        if not update.message:
            return
        if not context.args:
            await update.message.reply_text(
                "Пожалуйста, укажите текст для анализа.\n"
                "Пример: /analyze Ваш текст для анализа"
            )
            return

        text_to_analyze = " ".join(context.args)
        
        # Отправляем сообщение о том, что анализируем
        analyzing_message = await update.message.reply_text("🔍 Анализирую текст...")
        
        try:
            analysis = await self.gemini_client.analyze_text(text_to_analyze)
            await analyzing_message.edit_text(f"📊 *Анализ текста:*\n\n{analysis}", parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Ошибка при анализе текста: {e}")
            await analyzing_message.edit_text("❌ Произошла ошибка при анализе текста.")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка обычных текстовых сообщений"""
        if not update.message or not update.message.text:
            return
            
        user_message = update.message.text
        user_name = update.effective_user.first_name if update.effective_user else "Неизвестный"
        user_id = update.effective_user.id if update.effective_user else 0
        
        logger.info(f"Получено сообщение от {user_name} ({user_id}): {user_message[:50]}...")
        
        # Отправляем индикатор печатания
        if update.effective_chat:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        try:
            # Генерируем ответ с помощью Gemini
            response = await self.gemini_client.generate_response(user_message, user_name)
            
            # Отправляем ответ пользователю
            await update.message.reply_text(response)
            
            logger.info(f"Отправлен ответ пользователю {user_name} ({user_id})")
            
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")
            error_message = (
                "❌ Извините, произошла ошибка при обработке вашего сообщения.\n"
                "Пожалуйста, попробуйте позже или обратитесь к администратору."
            )
            await update.message.reply_text(error_message)

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logger.error(f"Произошла ошибка: {context.error}")
        
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже."
            )

    def run(self):
        """Запуск бота"""
        logger.info("Запуск Telegram бота...")
        
        # Добавляем обработчик ошибок
        self.application.add_error_handler(self.error_handler)
        
        # Запускаем бота
        try:
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)
        except Exception as e:
            logger.error(f"Критическая ошибка при запуске бота: {e}")
            raise
