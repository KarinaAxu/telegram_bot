import os
import django
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from asgiref.sync import sync_to_async

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tgbot.settings')
django.setup()

from tg.models import Post

MAIN_MENU_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["📝 Посмотреть посты", "✨ Добавить пост"],
        ["🔧 Изменить пост", "❌ Удалить пост"],
        ["❓ Помощь"]
    ],
    resize_keyboard=True
)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Приветик! 🐾 Чем могу помочь? Выберите действие:",
        reply_markup=MAIN_MENU_KEYBOARD
    )

# Обработчик просмотра постов
@sync_to_async
def get_post_list():
    posts = Post.objects.all().order_by('-created_date')
    if not posts:
        return "Постов пока нет. Напишите что-нибудь красивое! 🌸"
    return "\n".join([f"📌 {post.id}: {post.title} - {post.description[:50]}..." for post in posts])

async def list_posts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    post_list = await get_post_list()
    await update.message.reply_text(post_list)

# Создание поста
async def add_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Ожидаем ввод заголовка и описания в одном сообщении
    user_input = update.message.text.strip()

    if ',' not in user_input:
        await update.message.reply_text(
            "Неверный формат. Используйте: заголовок, описание 💔\nПример: Вечер, Какой красивый закат!"
        )
        return

    try:
        title, description = map(str.strip, user_input.split(",", 1))
        # Создаем пост в базе данных
        await sync_to_async(Post.objects.create)(title=title, description=description)
        await update.message.reply_text(f"Ура! Пост '{title}' добавлен! 🌟")
    except Exception as e:
        await update.message.reply_text("Что-то пошло не так. Попробуйте снова 🐾")

# Редактирование поста
async def edit_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Ожидаем ввод ID, нового заголовка и описания
    user_input = update.message.text.strip()

    if ',' not in user_input:
        await update.message.reply_text(
            "Неверный формат. Используйте: ID, заголовок, описание 💔\nПример: 1, Новый вечер, Новый красивый закат!"
        )
        return

    try:
        post_id, title, description = map(str.strip, user_input.split(",", 2))
        post_id = int(post_id)
        # Обновляем пост в базе данных
        post = await sync_to_async(Post.objects.filter(id=post_id).update)(title=title, description=description)
        if post:
            await update.message.reply_text(f"Пост с ID {post_id} обновлен! 🌟")
        else:
            await update.message.reply_text("Пост с таким ID не найден. 💔")
    except ValueError:
        await update.message.reply_text("ID должен быть числом. 💔")
    except Exception as e:
        await update.message.reply_text("Что-то пошло не так. Попробуйте снова 🐾")

# Удаление поста
async def delete_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Ожидаем ввод ID поста для удаления
    user_input = update.message.text.strip()

    try:
        post_id = int(user_input)
        # Удаляем пост
        post = await sync_to_async(Post.objects.filter(id=post_id).delete)()
        if post:
            await update.message.reply_text(f"Пост с ID {post_id} удален. 🗑️")
        else:
            await update.message.reply_text("Пост с таким ID не найден. 💔")
    except ValueError:
        await update.message.reply_text("ID должен быть числом. 💔")
    except Exception as e:
        await update.message.reply_text("Что-то пошло не так. Попробуйте снова 🐾")

# Помощь
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Это бот для управления постами!\n\n"
        "Вот что я могу:\n"
        "📝 Посмотреть посты — покажу все текущие посты.\n"
        "✨ Добавить пост — создайте новый пост, указав заголовок и описание.\n"
        "🔧 Изменить пост — обновите пост, указав ID, новый заголовок и описание.\n"
        "❌ Удалить пост — удалите пост по его ID.\n"
        "❓ Помощь — покажу эту информацию."
    )
    await update.message.reply_text(help_text)

# Создание и настройка бота
app = ApplicationBuilder().token("7757445345:AAG6WyTfCrClWs2-xMUb4vkV-gRgMFJ_qQg").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Text("📝 Посмотреть посты"), list_posts))
app.add_handler(MessageHandler(filters.Text("✨ Добавить пост"), add_post))
app.add_handler(MessageHandler(filters.Text("🔧 Изменить пост"), edit_post))
app.add_handler(MessageHandler(filters.Text("❌ Удалить пост"), delete_post))
app.add_handler(MessageHandler(filters.Text("❓ Помощь"), help))

if __name__ == "__main__":
    app.run_polling()