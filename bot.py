import logging
import os
import asyncio
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


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для управления задачами. Используй:\n"
        "- /add - добавить задачу\n"
        "- /list - показать список задач"
    )

async def add_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 Введите задачу:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    task_text = update.message.text
    add_task(user_id, task_text)
    await update.message.reply_text(f"✅ Добавлено: {task_text}")
    await list_tasks(update, context)

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = get_tasks(update.effective_user.id)
    if not tasks:
        await update.message.reply_text("📭 Список задач пуст!")
        return
    
    message = "📋 <b>Ваши задачи:</b>\n" + "\n".join(
        f"{'✅' if completed else '❌'} {text}"
        for _, text, completed in tasks
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_{id}"),
            InlineKeyboardButton("✅ Отметить", callback_data=f"toggle_{id}")
        ] for id, _, _ in tasks
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode='HTML')
    else:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data.startswith('delete_'):
        task_id = int(data.split('_')[1])
        delete_task(task_id, query.from_user.id)
        await query.answer("🗑️ Удалено!")
    elif data.startswith('toggle_'):
        task_id = int(data.split('_')[1])
        toggle_task(task_id, query.from_user.id)
        await query.answer("✅ Статус изменен!")
    
    await list_tasks(update, context)

def main():
    try:
        application = Application.builder().token(TOKEN).build()
        
        # Регистрация обработчиков
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("add", add_task_command))
        application.add_handler(CommandHandler("list", list_tasks))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(CallbackQueryHandler(button_callback))

        # Конфигурация для Render
        if os.getenv('ENVIRONMENT') == 'PROD':
            port = int(os.getenv('PORT', 10000))
            logger.info("🚀 Бот запущен в режиме PROD (Webhook)")
            
            application.run_webhook(
                listen="0.0.0.0",
                port=port,
                webhook_url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook",
                secret_token=os.getenv('WEBHOOK_SECRET'),
                drop_pending_updates=True
            )
        else:
            logger.info("🔍 Бот запущен в режиме DEV (Polling)")
            application.run_polling()
            
    except Exception as e:
        logger.critical(f"💥 Критическая ошибка: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    def main():
        application = Application.builder().token(TOKEN).build()
        
        # Регистрация обработчиков
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("add", add_task_command))
        application.add_handler(CommandHandler("list", list_tasks))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(CallbackQueryHandler(button_callback))

        # Вечный цикл для Render
        while True:
            try:
                if os.getenv('ENVIRONMENT') == 'PROD':
                    port = int(os.getenv('PORT', 10000))
                    logger.info("🔄 Запуск вебхука...")
                    application.run_webhook(
                        listen="0.0.0.0",
                        port=port,
                        webhook_url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook",
                        secret_token=os.getenv('WEBHOOK_SECRET'),
                        drop_pending_updates=True
                    )
                else:
                    application.run_polling()
            except Exception as e:
                logger.error(f"⚠️ Ошибка: {e}. Перезапуск через 5 секунд...")
                time.sleep(5)