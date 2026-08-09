import json
import os

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("TOKEN")

# Telegram user ID of the admin allowed to use admin commands
ADMIN_ID = 388368437  # Replace with your Telegram user ID

with open("voices.json", "r", encoding="utf-8") as file:
    voices = json.load(file)

VOICE_PER_PAGE = 5

def update_stats(title):
    try:
        with open("stats.json", "r", encoding="utf-8") as file:
            stats = json.load(file)
    except:
        stats = {}

    stats[title] = stats.get(title, 0) + 1

    with open("stats.json", "w", encoding="utf-8") as file:
        json.dump(stats, file, ensure_ascii=False, indent=4)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text(
            "❌ You don't have permission to use this command."
        )
        return

    try:
        with open("stats.json", "r", encoding="utf-8") as file:
            stats = json.load(file)
    except:
        stats = {}

    if not stats:
        await update.message.reply_text("📊 هنوز آماری ثبت نشده.")
        return

    sorted_stats = sorted(
        stats.items(),
        key=lambda x: x[1],
        reverse=True
    )

    message = "📊 Javidan Archive Stats\n\n"

    for i, (title, count) in enumerate(sorted_stats[:10], 1):
        message += f"{i}. {title}\n▶️ {count} requests\n\n"

    await update.message.reply_text(message)



def get_text(language, key):
    texts = {
        "فارسی": {
            "choose_category": "📂 دسته‌بندی را انتخاب کنید:",
            "choose_voice": "🎙 ویس مورد نظر را انتخاب کنید:",
            "change_language": "🌐 تغییر زبان",
            "back_categories": "🔙 بازگشت به دسته‌بندی‌ها",
            "next": "➡️ صفحه بعد",
            "previous": "⬅️ صفحه قبل"
        },
        "English": {
            "choose_category": "📂 Choose a category:",
            "choose_voice": "🎙 Choose a voice:",
            "change_language": "🌐 Change Language",
            "back_categories": "🔙 Back to Categories",
            "next": "➡️ Next Page",
            "previous": "⬅️ Previous Page"
        }
    }
    return texts[language][key]


def language_menu():
    return ReplyKeyboardMarkup(
        [[KeyboardButton(lang)] for lang in voices.keys()],
        resize_keyboard=True
    )


def category_menu(language):
    buttons = [
        [KeyboardButton(category)]
        for category in voices[language].keys()
    ]

    buttons.append(
        [KeyboardButton(get_text(language, "change_language"))]
    )

    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def voice_menu(language, category, page):
    titles = list(voices[language][category]["voices"].keys())

    start = page * VOICE_PER_PAGE
    end = start + VOICE_PER_PAGE

    buttons = [
        [KeyboardButton(title)]
        for title in titles[start:end]
    ]

    navigation = []

    if end < len(titles):
        navigation.append(KeyboardButton(get_text(language, "next")))

    if page > 0:
        navigation.append(KeyboardButton(get_text(language, "previous")))

    if navigation:
        buttons.append(navigation)

    buttons.append(
        [KeyboardButton(get_text(language, "back_categories"))]
    )

    buttons.append(
        [KeyboardButton(get_text(language, "change_language"))]
    )

    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        """🏛 Javidan Archive

آرشیو کامل ویس‌های فارسی و انگلیسی کانال جاویدان

Choose your language:""",
        reply_markup=language_menu()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """📚 راهنمای استفاده از آرشیو جاویدان

1️⃣ زبان را انتخاب کنید.
2️⃣ دسته‌بندی را انتخاب کنید.
3️⃣ روی عنوان ویس کلیک کنید.

برای شروع دوباره:
 /start"""
    )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """🏛 Javidan Archive

آرشیو سازمان‌یافته ویس‌های کانال جاویدان.

Available languages:
• فارسی
• English"""
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    language = context.user_data.get("language")

    if text in ["🌐 تغییر زبان", "🌐 Change Language"]:
        context.user_data.clear()
        await update.message.reply_text(
            "🌐 Choose Language:",
            reply_markup=language_menu()
        )
        return

    if text in voices:
        context.user_data["language"] = text
        await update.message.reply_text(
            get_text(text, "choose_category"),
            reply_markup=category_menu(text)
        )
        return

    if not language:
        return

    if text in ["🔙 بازگشت به دسته‌بندی‌ها", "🔙 Back to Categories"]:
        context.user_data.pop("category", None)
        await update.message.reply_text(
            get_text(language, "choose_category"),
            reply_markup=category_menu(language)
        )
        return

    if text in voices[language]:
        context.user_data["category"] = text
        context.user_data["page"] = 0

        await update.message.reply_text(
            get_text(language, "choose_voice"),
            reply_markup=voice_menu(language, text, 0)
        )
        return

    category = context.user_data.get("category")

    if text in [get_text(language, "next"), get_text(language, "previous")]:
        page = context.user_data.get("page", 0)

        if text == get_text(language, "next"):
            page += 1
        else:
            page = max(0, page - 1)

        context.user_data["page"] = page

        await update.message.reply_text(
            f"📄 Page {page + 1}",
            reply_markup=voice_menu(language, category, page)
        )
        return

    if category and text in voices[language][category]["voices"]:
        file_data = voices[language][category]["voices"][text]

        update_stats(text)

        caption = f"""🎙 {text}

📂 {category}"""

        if file_data.get("link"):
            caption += f"""

🔗 Original:
{file_data['link']}"""

        caption += """

🏛 @Javidan Archive"""

        try:
            if file_data["type"] == "voice":
                await update.message.reply_voice(
                    voice=file_data["id"],
                    caption=caption
                )
            else:
                await update.message.reply_audio(
                    audio=file_data["id"],
                    caption=caption
                )

        except Exception as e:
            print("SEND ERROR:", e)
            await update.message.reply_text(
                "❌ ارسال فایل با مشکل مواجه شد."
            )


async def error_handler(update, context):
    print("ERROR:", context.error)


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("about", about_command))
app.add_handler(CommandHandler("stats", stats_command))

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
)

app.add_error_handler(error_handler)

print("Bot running...")
app.run_polling()
