# 🚀 Быстрый запуск бота

## Что нужно сделать:

### 1. Скачайте файлы:
- `simple_bot.py` - основной файл бота  
- `example.env` - пример настроек

### 2. Установите Python библиотеки:
```bash
pip install python-telegram-bot google-genai python-dotenv
```

### 3. Получите API ключи:

**Telegram Bot:**
- Напишите @BotFather в Telegram
- Отправьте `/newbot` и следуйте инструкциям  
- Скопируйте токен (выглядит как `123456789:ABCdefGHI...`)

**Gemini AI:**
- Идите на https://aistudio.google.com/
- Войдите через Google аккаунт
- Нажмите "Get API Key" и создайте ключ

### 4. Создайте файл `.env`:
```
TELEGRAM_BOT_TOKEN=ваш_токен_здесь
GEMINI_API_KEY=ваш_ключ_здесь
```

### 5. Запустите бота:
```bash
python simple_bot.py
```

## ✅ Готово!

Теперь найдите вашего бота в Telegram и напишите ему сообщение. Он будет отвечать через Gemini AI.

**Для остановки:** нажмите `Ctrl+C`