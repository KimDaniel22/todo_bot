import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from database import init_db, add_task, get_tasks, delete_task, toggle_task
from config import TOKEN

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text("Привет! Я бот для управления задачами. Используй /help для списка команд.")

# ... (остальные обработчики из предыдущего кода остаются без изменений)

def main():
    """Запуск приложения"""
    application = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_task_command))
    application.add_handler(CommandHandler("list", list_tasks))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Webhook configuration
    webhook_url = "https://your-service-name.onrender.com/webhook"
    
    # Для локального тестирования используем polling
    if os.getenv('ENVIRONMENT') == 'DEV':
        application.run_polling()
    else:
        # Настройка для Render
        port = int(os.environ.get("PORT", 10000))
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            webhook_url=webhook_url
        )

if __name__ == '__main__':
    main()