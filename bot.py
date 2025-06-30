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

# Инициализация базы данных
init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    welcome_message = (
        f"Привет, {user.first_name}! 👋\n\n"
        "Я бот для управления задачами. Вот что я умею:\n"
        "- /add - добавить новую задачу\n"
        "- /list - показать список задач\n"
        "- Просто напиши мне задачу, и я её добавлю"
    )
    await update.message.reply_text(welcome_message)

async def add_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /add"""
    await update.message.reply_text("Напиши задачу, которую нужно добавить:")

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список задач с кнопками управления"""
    user_id = update.effective_user.id
    tasks = get_tasks(user_id)
    
    if not tasks:
        await update.message.reply_text("У тебя пока нет задач! 😊")
        return
    
    message = "📝 <b>Твой список задач:</b>\n\n"
    keyboard = []
    
    for task_id, task_text, is_completed in tasks:
        status = "✅" if is_completed else "❌"
        message += f"{status} {task_text}\n"
        
        # Добавляем кнопки для каждой задачи
        keyboard.append([
            InlineKeyboardButton(
                "🗑️ Удалить",
                callback_data=f"delete_{task_id}"
            ),
            InlineKeyboardButton(
                "✅ Отметить" if not is_completed else "❌ Снять отметку",
                callback_data=f"toggle_{task_id}"
            )
        ])
    
    # Добавляем кнопку обновления списка
    keyboard.append([InlineKeyboardButton("🔄 Обновить список", callback_data="refresh")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Если это обновление существующего сообщения
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=message, 
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            message, 
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает текстовые сообщения как новые задачи"""
    user_id = update.effective_user.id
    task_text = update.message.text
    
    if task_text.startswith('/'):
        return
    
    add_task(user_id, task_text)
    await update.message.reply_text(f"✅ Задача добавлена: {task_text}")
    await list_tasks(update, context)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатия на inline-кнопки"""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    
    await query.answer()
    
    if data.startswith('delete_'):
        task_id = int(data.split('_')[1])
        delete_task(task_id, user_id)
        await query.edit_message_text(text="🗑️ Задача удалена!")
        await list_tasks(update, context)
    
    elif data.startswith('toggle_'):
        task_id = int(data.split('_')[1])
        toggle_task(task_id, user_id)
        await query.answer("Статус задачи обновлён!")
        await list_tasks(update, context)
    
    elif data == 'refresh':
        await query.answer("Список обновлён!")
        await list_tasks(update, context)

def main():
    """Запускает бота"""
    application = Application.builder().token(TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_task_command))
    application.add_handler(CommandHandler("list", list_tasks))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    

    application.run_polling()

if __name__ == '__main__':
    main()