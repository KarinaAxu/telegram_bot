import os
import django
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tgbot.settings')
django.setup()

from tg.models import Post

@sync_to_async
def create_post_in_db(title, description, author_id):
    user = get_user_model().objects.get(telegram_id=author_id)
    return Post.objects.create(title=title, description=description, author=user)

@sync_to_async
def check_user_exists(user_id):
    return get_user_model().objects.filter(telegram_id=user_id).exists()

@sync_to_async
def create_user(user_id, username):
    return get_user_model().objects.create(telegram_id=user_id, username=username)

@sync_to_async
def get_user_posts(user_id):
    return list(Post.objects.filter(author_id=user_id).values("id", "title", "description"))

@sync_to_async
def delete_post(post_id):
    return Post.objects.filter(id=post_id).delete()

@sync_to_async
def get_post_by_id(post_id):
    return Post.objects.filter(id=post_id).values("id", "title", "description").first()

async def start(update: Update, context):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "солнышко"
    if not await check_user_exists(user_id):
        await create_user(user_id, username)
        await update.message.reply_text(f"Добро пожаловать, {username}! 🌸 Ты теперь часть нашей команды!")
    await update.message.reply_text(
        "Привет-привет! 🐾 Я твой бот-помощник для управления постами. Вот мои команды:\n\n"
        "✨ /start - Начать наше приключение\n"
        "🌈 /help - Узнать мои умения\n"
        "📋 /create - Создать новый пост\n"
        "🖊️ /edit - Изменить пост\n"
        "🗑️ /delete - Удалить пост\n"
        "📑 /view - Просмотреть все свои посты\n\n"
        "Давай творить магию вместе! ✨"
    )

async def help_command(update: Update, context):
    await update.message.reply_text(
        "Я умею:\n"
        "🌟 /create - Создавать новые посты\n"
        "💡 /edit - Редактировать посты\n"
        "🗑️ /delete - Удалять посты\n"
        "📑 /view - Просматривать все свои посты\n\n"
        "Если есть вопросы, просто зови меня! 🌷"
    )

async def create_command(update: Update, context):
    user_id = update.message.from_user.id
    if not await check_user_exists(user_id):
        await update.message.reply_text("Пользователь не найден. Зарегистрируйтесь через /start.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Пожалуйста, укажите название и описание через пробел: `/create Название Описание`")
        return
    title, description = context.args[0], " ".join(context.args[1:])
    await create_post_in_db(title, description, user_id)
    await update.message.reply_text(f"Пост '{title}' создан! 🎉")

async def list_posts(update: Update, context):
    user_id = update.message.from_user.id
    posts = await get_user_posts(user_id)
    if not posts:
        await update.message.reply_text("У вас пока нет постов. Создайте первый с помощью команды /create!")
        return
    buttons = [
        [InlineKeyboardButton(post["title"], callback_data=f"view_post_{post['id']}"),
         InlineKeyboardButton("Редактировать", callback_data=f"edit_post_{post['id']}"),
         InlineKeyboardButton("Удалить", callback_data=f"delete_post_{post['id']}")]
        for post in posts
    ]
    markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Ваши посты:", reply_markup=markup)

async def view_posts(update: Update, context):
    user_id = update.message.from_user.id
    posts = await get_user_posts(user_id)
    if not posts:
        await update.message.reply_text("У вас пока нет постов. Создайте первый с помощью команды /create!")
        return
    posts_text = "\n\n".join([f"📋 {post['title']}: {post['description']}" for post in posts])
    await update.message.reply_text(f"Ваши посты:\n\n{posts_text}")

async def handle_post_actions(update: Update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("view_post_"):
        post_id = int(data.split("_")[2])
        post = await get_post_by_id(post_id)
        if post:
            await query.message.reply_text(f"📋 Пост: {post['title']}\n\n{post['description']}")
        else:
            await query.message.reply_text("Пост не найден.")
    elif data.startswith("edit_post_"):
        post_id = int(data.split("_")[2])
        post = await get_post_by_id(post_id)
        if post:
            await query.message.reply_text(f"Редактирование поста: {post['title']}\n\nОписание: {post['description']}\nВведите новое описание.")
        else:
            await query.message.reply_text("Пост не найден.")
    elif data.startswith("delete_post_"):
        post_id = int(data.split("_")[2])
        await delete_post(post_id)
        await query.message.reply_text("Пост удален. 🗑️")

async def handle_edit(update: Update, context):
    user_id = update.message.from_user.id
    if len(context.args) < 2:
        await update.message.reply_text("Пожалуйста, укажите ID поста и новый текст: `/edit ID новый текст`.")
        return
    post_id = int(context.args[0])
    new_description = " ".join(context.args[1:])
    post = await get_post_by_id(post_id)
    if post:
        post['description'] = new_description
        Post.objects.filter(id=post_id).update(description=new_description)  # Обновляем описание в базе
        await update.message.reply_text(f"Пост '{post['title']}' обновлен! 🌟")
    else:
        await update.message.reply_text("Пост не найден.")

def main():
    app = ApplicationBuilder().token("7757445345:AAG6WyTfCrClWs2-xMUb4vkV-gRgMFJ_qQg").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("create", create_command))
    app.add_handler(CommandHandler("list", list_posts))
    app.add_handler(CommandHandler("view", view_posts))
    app.add_handler(CallbackQueryHandler(handle_post_actions))
    app.add_handler(CommandHandler("edit", handle_edit))
    print("Бот запущен... 🐾")
    app.run_polling()

if __name__ == "__main__":
    main()