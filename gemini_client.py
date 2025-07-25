import logging
import os
from google import genai  # type: ignore
from google.genai import types
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        """Инициализация клиента Gemini AI"""
        try:
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            logger.info("Gemini клиент успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации Gemini клиента: {e}")
            raise

    async def generate_response(self, user_message: str, user_name: str | None = None) -> str:
        """
        Генерирует ответ на сообщение пользователя
        
        Args:
            user_message (str): Сообщение пользователя
            user_name (str): Имя пользователя (опционально)
            
        Returns:
            str: Ответ от Gemini AI
        """
        try:
            # Формируем контекстный промпт
            context = "Ты дружелюбный AI-ассистент в Telegram боте. "
            context += "Отвечай на русском языке, будь полезным и вежливым. "
            
            if user_name:
                context += f"Пользователя зовут {user_name}. "
            
            prompt = f"{context}\n\nВопрос пользователя: {user_message}"
            
            logger.info(f"Отправляем запрос в Gemini для пользователя {user_name or 'Неизвестный'}")
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            if response.text:
                logger.info("Получен успешный ответ от Gemini")
                return response.text
            else:
                logger.warning("Получен пустой ответ от Gemini")
                return "Извините, я не смог сгенерировать ответ на ваш вопрос. Попробуйте переформулировать."
                
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа: {e}")
            return "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже."

    async def analyze_text(self, text: str) -> str:
        """
        Анализирует текст и предоставляет краткое резюме
        
        Args:
            text (str): Текст для анализа
            
        Returns:
            str: Анализ текста
        """
        try:
            prompt = f"Проанализируй следующий текст и предоставь краткое резюме на русском языке:\n\n{text}"
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return response.text or "Не удалось проанализировать текст."
            
        except Exception as e:
            logger.error(f"Ошибка при анализе текста: {e}")
            return "Произошла ошибка при анализе текста."
