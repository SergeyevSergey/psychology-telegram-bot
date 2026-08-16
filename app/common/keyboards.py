from telegram import InlineKeyboardMarkup, InlineKeyboardButton


main_menu = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("💾 Файлы", callback_data=f"files:categories")],
        [InlineKeyboardButton("💬 Вопрос / предложение", callback_data="feedbacks:create")],
        [InlineKeyboardButton("📊 Опросы", callback_data=f"polls:page:{0}")],
        [InlineKeyboardButton("ℹ️ О проекте", callback_data="about")],
    ]
)


admin_menu = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("💾 Файлы", callback_data="files:admin_menu")],
        [InlineKeyboardButton("🗂 Категории", callback_data="categories:admin_menu")],
        [InlineKeyboardButton("📩 Сообщения", callback_data=f"feedbacks:page:{0}")],
        [InlineKeyboardButton("📊 Опросы", callback_data="polls:admin_menu")],
        [InlineKeyboardButton("📈 Статистика", callback_data="stats")],
    ]
)
