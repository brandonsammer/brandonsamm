# Telegram Bot with Google Gemini AI Integration

## Overview

This project is a Telegram bot that integrates with Google Gemini AI to provide intelligent conversational capabilities. The bot can respond to user messages, answer questions, help with various tasks, and analyze texts using Google's Gemini AI model.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

- **Bot Layer (`bot.py`)**: Handles Telegram bot functionality and user interactions
- **AI Client Layer (`gemini_client.py`)**: Manages communication with Google Gemini AI
- **Configuration Layer (`config.py`)**: Centralizes environment variable management
- **Entry Point (`main.py`)**: Application bootstrap and logging setup

The architecture is designed as a lightweight, stateless service that processes incoming Telegram messages and generates AI-powered responses.

## Key Components

### 1. TelegramBot Class (`bot.py`)
- **Purpose**: Main bot controller that handles Telegram webhook events
- **Features**: Command handling (/start, /help, /analyze), message processing
- **Dependencies**: python-telegram-bot library, GeminiClient

### 2. GeminiClient Class (`gemini_client.py`)
- **Purpose**: Abstraction layer for Google Gemini AI API
- **Features**: Response generation with contextual prompts, error handling
- **Model**: Uses "gemini-2.5-flash" for text generation

### 3. Configuration Management (`config.py`)
- **Purpose**: Environment variable loading and validation
- **Required Variables**: TELEGRAM_BOT_TOKEN, GEMINI_API_KEY
- **Features**: Automatic validation of required environment variables

### 4. Application Entry Point (`main.py`)
- **Purpose**: Application initialization and lifecycle management
- **Features**: Comprehensive logging setup, graceful shutdown handling

## Data Flow

1. **User Input**: User sends message to Telegram bot
2. **Message Processing**: Bot receives update via Telegram API
3. **Context Building**: System constructs contextual prompt with user message
4. **AI Processing**: Request sent to Google Gemini AI with Russian language context
5. **Response Generation**: Gemini AI generates appropriate response
6. **Message Delivery**: Bot sends response back to user via Telegram API

The system is stateless - each message is processed independently without persistent session storage.

## External Dependencies

### APIs and Services
- **Telegram Bot API**: For receiving and sending messages
- **Google Gemini AI API**: For natural language processing and response generation

### Python Libraries
- `python-telegram-bot`: Telegram bot framework
- `google-genai`: Google Gemini AI client library
- `python-dotenv`: Environment variable management
- `asyncio`: Asynchronous programming support

### Environment Variables
- `TELEGRAM_BOT_TOKEN`: Required for Telegram API authentication
- `GEMINI_API_KEY`: Required for Google Gemini AI access
- `LOG_LEVEL`: Optional logging configuration

## Deployment Strategy

### Current Setup
- **Runtime**: Python 3.x application
- **Configuration**: Environment variable based
- **Logging**: File-based logging (`bot.log`) with console output
- **Error Handling**: Comprehensive exception handling with graceful degradation

### Deployment Considerations
- Requires external API access (Telegram, Google)
- Stateless design enables horizontal scaling
- No database requirements - fully API-driven
- Suitable for containerized deployment
- Supports graceful shutdown via keyboard interrupt

### Scaling Options
- Can be deployed as single instance for low traffic
- Horizontal scaling possible due to stateless nature
- Consider rate limiting for API calls in high-traffic scenarios
- Monitor API quotas for both Telegram and Gemini services