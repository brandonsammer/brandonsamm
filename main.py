import argparse
import asyncio
import io
import os
import traceback
import time
import google.genai as genai
from telebot import types as telebot_types
from telebot.async_telebot import AsyncTeleBot
from md2tgmd import escape
from PIL import Image
from flask import Flask, request

conf = {
    "error_info": "⚠️⚠️⚠️\nЧто-то пошло не так!\nПопробуйте изменить запрос или свяжитесь с администратором!",
    "before_generate_info": "🤖 Генерирую...",
    "download_pic_notify": "🤖 Загружаю изображение...",
    "model_1": "gemini-1.5-flash-latest",
    "model_2": "gemini-1.5-pro-latest",
    "model_3": "gemini-1.5-flash-latest",
    "streaming_update_interval": 1.0,
    "help_text":
        """
        *Добро пожаловать! Вот список доступных команд:*

        `/gemini <сообщение>` — Задать вопрос модели Gemini Flash.
        `/gemini_pro <сообщение>` — Задать вопрос модели Gemini Pro.
        `/draw <промпт>` — Сгенерировать изображение по тексту.
        `/edit <промпт>` — Отредактировать фото (ответом на сообщение с фото).
        `/clear` — Очистить историю вашей переписки.
        `/switch` — Переключить модель по умолчанию для личных чатов.
        `/help` — Показать эту справку.

        *Для использования модели по умолчанию просто отправьте сообщение в личный чат.*
        *Для редактирования, ответьте на фото командой: `/edit Сделай небо синим`.*
        """,
}

safety_settings = [
    genai.types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
    genai.types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
    genai.types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
    genai.types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
]

generation_config = genai.types.GenerationConfig(safety_settings=safety_settings)

if os.environ.get("RENDER"):
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
else:
    parser = argparse.ArgumentParser(description="Gemini Telegram Bot")
    parser.add_argument("tg_token", help="Telegram Bot token")
    parser.add_argument("GOOGLE_GEMINI_KEY", help="Google Gemini API Key")
    options = parser.parse_args()
    TELEGRAM_TOKEN = options.tg_token
    GEMINI_API_KEY = options.GOOGLE_GEMINI_KEY

gemini_chat_dict = {}
gemini_pro_chat_dict = {}
default_model_dict = {}

genai.configure(api_key=GEMINI_API_KEY)
bot = AsyncTeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

async def gemini_stream(message: telebot_types.Message, m: str, model_type: str):
    sent_message = None
    try:
        chat_dict = gemini_chat_dict if model_type == conf["model_1"] else gemini_pro_chat_dict
        user_id = str(message.from_user.id)
        chat = chat_dict.get(user_id)
        if not chat:
            model = genai.GenerativeModel(model_name=model_type, tools=['google_search'])
            chat = model.start_chat()
            chat_dict[user_id] = chat
        
        sent_message = await bot.reply_to(message, conf["before_generate_info"])
        response_stream = await chat.send_message_async(m, stream=True)
        full_response = ""
        last_update = time.time()
        
        async for chunk in response_stream:
            if chunk.text:
                full_response += chunk.text
                if time.time() - last_update >= conf["streaming_update_interval"]:
                    try:
                        await bot.edit_message_text(
                            escape(full_response + " ▌"),
                            chat_id=sent_message.chat.id,
                            message_id=sent_message.message_id,
                            parse_mode="MarkdownV2"
                        )
                        last_update = time.time()
                    except Exception as e:
                        if "message is not modified" not in str(e).lower():
                             print(f"Update error: {e}")
        
        final_text = escape(full_response) if full_response else "Empty response from API."
        await bot.edit_message_text(
            final_text,
            chat_id=sent_message.chat.id,
            message_id=sent_message.message_id,
            parse_mode="MarkdownV2"
        )
    except Exception:
        traceback.print_exc()
        if sent_message:
            await bot.edit_message_text(conf['error_info'], chat_id=sent_message.chat.id, message_id=sent_message.message_id)
        else:
            await bot.reply_to(message, conf['error_info'])

async def gemini_edit(message: telebot_types.Message, m: str, photo_file: bytes):
    try:
        image = Image.open(io.BytesIO(photo_file))
        model = genai.GenerativeModel(conf["model_3"])
        response = await model.generate_content_async([m, image], generation_config=generation_config)
        if response.parts and hasattr(response.parts[0], 'text'):
            await bot.reply_to(message, escape(response.text), parse_mode="MarkdownV2")
        else:
            await gemini_draw(message, "based on the image and this prompt: " + m)
    except Exception:
        traceback.print_exc()
        await bot.reply_to(message, conf['error_info'])

async def gemini_draw(message: telebot_types.Message, m: str):
    try:
        model = genai.GenerativeModel(conf["model_3"])
        response = await model.generate_content_async(
            "Нарисуй: " + m, 
            generation_config=generation_config
        )
        photo_data = response.parts[0].inline_data.data
        await bot.send_photo(message.chat.id, photo_data, caption="Сгенерировано ✨", reply_to_message_id=message.message_id)
    except Exception:
        traceback.print_exc()
        await bot.reply_to(message, conf['error_info'])

async def help_command(message: telebot_types.Message):
    await bot.reply_to(message, conf["help_text"], parse_mode="MarkdownV2", disable_web_page_preview=True)

async def start(message: telebot_types.Message):
    await bot.reply_to(message, escape("Привет! Я бот на базе Gemini. Используйте /help, чтобы увидеть все команды."), parse_mode="MarkdownV2")

async def get_text_from_command(message_text, command):
    return message_text.strip().split(command, 1)[1].strip()

async def gemini_handler_template(message, model_name, command_name):
    try:
        m = await get_text_from_command(message.text, command_name)
        if not m: raise IndexError
        await bot.send_chat_action(message.chat.id, 'typing')
        await gemini_stream(message, m, model_name)
    except IndexError:
        await bot.reply_to(message, escape(f"Пожалуйста, добавьте текст после команды.\nПример: `/{command_name} Кто такой Илон Маск?`"), parse_mode="MarkdownV2")

async def gemini_stream_handler(message: telebot_types.Message):
    await gemini_handler_template(message, conf["model_1"], "/gemini")
    
async def gemini_pro_stream_handler(message: telebot_types.Message):
    await gemini_handler_template(message, conf["model_2"], "/gemini_pro")

async def clear(message: telebot_types.Message):
    user_id = str(message.from_user.id)
    if user_id in gemini_chat_dict: del gemini_chat_dict[user_id]
    if user_id in gemini_pro_chat_dict: del gemini_pro_chat_dict[user_id]
    await bot.reply_to(message, "Ваша история переписки очищена.")

async def switch(message: telebot_types.Message):
    if message.chat.type != "private":
        await bot.reply_to(message, "Эта команда доступна только в личных чатах!")
        return
    user_id = str(message.from_user.id)
    current_status = default_model_dict.get(user_id, True)
    default_model_dict[user_id] = not current_status
    model_now = conf['model_1'] if default_model_dict[user_id] else conf['model_2']
    await bot.reply_to(message, f"Модель по умолчанию изменена на: `{model_now}`")

async def gemini_private_handler(message: telebot_types.Message):
    await bot.send_chat_action(message.chat.id, 'typing')
    user_id = str(message.from_user.id)
    model_to_use = conf["model_1"] if default_model_dict.get(user_id, True) else conf["model_2"]
    await gemini_stream(message, message.text.strip(), model_to_use)

async def edit_or_draw_handler(message: telebot_types.Message, command_name):
    if command_name == "/edit" and (not message.reply_to_message or not message.reply_to_message.photo):
        await bot.reply_to(message, "Нужно ответить на сообщение с фотографией, чтобы отредактировать его.")
        return
    try:
        m = await get_text_from_command(message.text, command_name)
        if not m: raise IndexError
        if command_name == "/draw":
            await bot.send_chat_action(message.chat.id, 'upload_photo')
            msg = await bot.reply_to(message, "🎨 Рисую...")
            await gemini_draw(message, m)
            await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
        elif command_name == "/edit":
            await bot.send_chat_action(message.chat.id, 'typing')
            file_id = message.reply_to_message.photo[-1].file_id
            file_info = await bot.get_file(file_id)
            photo_file = await bot.download_file(file_info.file_path)
            await gemini_edit(message, m, photo_file)
    except IndexError:
        await bot.reply_to(message, escape(f"Пожалуйста, добавьте описание после команды `/{command_name}`."), parse_mode="MarkdownV2")
    except Exception:
        traceback.print_exc()
        await bot.reply_to(message, conf['error_info'])

async def draw_handler(m: telebot_types.Message): await edit_or_draw_handler(m, "/draw")
async def edit_handler(m: telebot_types.Message): await edit_or_draw_handler(m, "/edit")

bot.register_message_handler(start, commands=['start'], pass_bot=False)
bot.register_message_handler(help_command, commands=['help'], pass_bot=False)
bot.register_message_handler(gemini_stream_handler, commands=['gemini'], pass_bot=False)
bot.register_message_handler(gemini_pro_stream_handler, commands=['gemini_pro'], pass_bot=False)
bot.register_message_handler(draw_handler, commands=['draw'], pass_bot=False)
bot.register_message_handler(edit_handler, commands=['edit'], pass_bot=False)
bot.register_message_handler(clear, commands=['clear'], pass_bot=False)
bot.register_message_handler(switch, commands=['switch'], pass_bot=False)
bot.register_message_handler(gemini_private_handler, func=lambda m: m.chat.type == "private" and not m.text.startswith('/'), content_types=['text'], pass_bot=False)

@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot_types.Update.de_json(json_string)
        asyncio.run(bot.process_new_updates([update]))
        return '', 200
    return 'Unsupported Media Type', 415

async def run_bot():
    if os.environ.get("RENDER"):
        print("Starting bot in webhook mode for Render...")
        webhook_url = os.environ.get("RENDER_EXTERNAL_URL")
        await bot.remove_webhook()
        await bot.set_webhook(url=f"{webhook_url}/{TELEGRAM_TOKEN}")
        print(f"Webhook has been set to {webhook_url}")
    else:
        print("Starting bot in polling mode for local development...")
        await bot.remove_webhook()
        await bot.polling(non_stop=True)

if __name__ == '__main__':
    if not os.environ.get("RENDER"):
        asyncio.run(run_bot())