import os
from dotenv import load_dotenv
import asyncio
import telebot
from telebot.async_telebot import AsyncTeleBot
import handlers
from config import conf

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_API_KEY")

if not TELEGRAM_TOKEN:
    print("Ошибка: Не найден токен TELEGRAM_BOT_API_KEY. Убедитесь, что вы задали его в переменных окружения.")
    exit()

async def main():
    bot = AsyncTeleBot(TELEGRAM_TOKEN)
    await bot.delete_my_commands(scope=None, language_code=None)
    await bot.set_my_commands(
    commands=[
        telebot.types.BotCommand("start", "Start the bot"),
        telebot.types.BotCommand("gemini", f"Chat using {conf['model_1']}"),
        telebot.types.BotCommand("gemini_pro", f"Chat using {conf['model_2']}"),
        telebot.types.BotCommand("draw", "Generate an image"),
        telebot.types.BotCommand("edit", "Edit a photo"),
        telebot.types.BotCommand("clear", "Clear chat history"),
        telebot.types.BotCommand("switch","Switch default model in private chat")
    ],
)
    print("Bot init done.")

    bot.register_message_handler(handlers.start,                         commands=['start'],         pass_bot=True)
    bot.register_message_handler(handlers.gemini_stream_handler,         commands=['gemini'],        pass_bot=True)
    bot.register_message_handler(handlers.gemini_pro_stream_handler,     commands=['gemini_pro'],    pass_bot=True)
    bot.register_message_handler(handlers.draw_handler,                  commands=['draw'],          pass_bot=True)
    bot.register_message_handler(handlers.gemini_edit_handler,           commands=['edit'],          pass_bot=True)
    bot.register_message_handler(handlers.clear,                         commands=['clear'],         pass_bot=True)
    bot.register_message_handler(handlers.switch,                        commands=['switch'],        pass_bot=True)
    bot.register_message_handler(handlers.gemini_photo_handler,          content_types=["photo"],    pass_bot=True)
    bot.register_message_handler(
        handlers.gemini_private_handler,
        func=lambda message: message.chat.type == "private",
        content_types=['text'],
        pass_bot=True)

    print("Starting Gemini_Telegram_Bot...")
    await bot.polling(none_stop=True)

if __name__ == '__main__':
    asyncio.run(main())