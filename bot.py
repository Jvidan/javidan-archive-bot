import json

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)


import os

TOKEN = os.environ.get("TOKEN")

if not TOKEN:
    raise Exception("TOKEN IS MISSING")


with open("voices.json", "r", encoding="utf-8") as file:
    voices = json.load(file)


VOICE_PER_PAGE = 5



# =========================
# Texts
# =========================

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



# =========================
# Keyboards
# =========================


def language_menu():

    buttons = []

    for language in voices.keys():

        buttons.append(
            [KeyboardButton(language)]
        )


    return ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True
    )




def category_menu(language):

    buttons = []


    for category in voices[language].keys():

        buttons.append(
            [KeyboardButton(category)]
        )


    buttons.append(
        [
            KeyboardButton(
                get_text(language, "change_language")
            )
        ]
    )


    return ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True
    )




def voice_menu(language, category, page):

    titles = list(
        voices[language][category]["voices"].keys()
    )


    start = page * VOICE_PER_PAGE
    end = start + VOICE_PER_PAGE


    buttons = []


    for title in titles[start:end]:

        buttons.append(
            [KeyboardButton(title)]
        )



    navigation = []


    if end < len(titles):

        navigation.append(
            KeyboardButton(
                get_text(language, "next")
            )
        )


    if page > 0:

        navigation.append(
            KeyboardButton(
                get_text(language, "previous")
            )
        )


    if navigation:

        buttons.append(navigation)



    buttons.append(
        [
            KeyboardButton(
                get_text(language, "back_categories")
            )
        ]
    )


    buttons.append(
        [
            KeyboardButton(
                get_text(language, "change_language")
            )
        ]
    )


    return ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True
    )# =========================
# Commands
# =========================


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()


    await update.message.reply_text(
        """
🏛 Javidan Archive

آرشیو کامل ویس‌های فارسی و انگلیسی کانال جاویدان

لطفاً زبان را انتخاب کنید:
        
Choose your language:
        """,
        reply_markup=language_menu()
    )



async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        """
📚 راهنمای استفاده از آرشیو جاویدان

1️⃣ زبان مورد نظر خود را انتخاب کنید.
2️⃣ وارد دسته‌بندی شوید.
3️⃣ روی عنوان ویس کلیک کنید تا فایل صوتی ارسال شود.

دسته‌بندی‌ها:

🏛 فلسفه و سیاست
💼 کسب و کار

برای شروع دوباره:
 /start
        """
    )



async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        """
🏛 درباره آرشیو جاویدان

این ربات یک آرشیو سازمان‌یافته از فایل‌های صوتی کانال جاویدان است.

موضوعات:

• فلسفه
• سیاست
• کسب و کار
• فناوری و آینده

محتوا در دو زبان فارسی و انگلیسی در دسترس است.

Javidan Archive
        """
    )





# =========================
# Message Handler
# =========================


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text


    language = context.user_data.get("language")



    # Change language

    if text in [
        "🌐 تغییر زبان",
        "🌐 Change Language"
    ]:

        context.user_data.clear()


        await update.message.reply_text(
            "🌐 زبان را انتخاب کنید / Choose Language:",
            reply_markup=language_menu()
        )

        return




    # Select language

    if text in voices:

        context.user_data["language"] = text


        await update.message.reply_text(
            get_text(text, "choose_category"),
            reply_markup=category_menu(text)
        )

        return




    if not language:

        return




    # Back to categories

    if text in [
        "🔙 بازگشت به دسته‌بندی‌ها",
        "🔙 Back to Categories"
    ]:

        context.user_data.pop("category", None)
        context.user_data["page"] = 0


        await update.message.reply_text(
            get_text(language, "choose_category"),
            reply_markup=category_menu(language)
        )

        return




    # Category selection

    if text in voices[language]:

        context.user_data["category"] = text
        context.user_data["page"] = 0


        await update.message.reply_text(
            get_text(language, "choose_voice"),
            reply_markup=voice_menu(
                language,
                text,
                0
            )
        )

        return    # Next page

    if text in [
        "➡️ صفحه بعد",
        "➡️ Next Page"
    ]:

        category = context.user_data.get("category")

        page = context.user_data.get(
            "page",
            0
        )

        page += 1

        context.user_data["page"] = page


        await update.message.reply_text(
            f"📄 Page {page + 1}",
            reply_markup=voice_menu(
                language,
                category,
                page
            )
        )

        return




    # Previous page

    if text in [
        "⬅️ صفحه قبل",
        "⬅️ Previous Page"
    ]:

        category = context.user_data.get("category")

        page = context.user_data.get(
            "page",
            0
        )


        page -= 1


        if page < 0:
            page = 0


        context.user_data["page"] = page


        await update.message.reply_text(
            f"📄 Page {page + 1}",
            reply_markup=voice_menu(
                language,
                category,
                page
            )
        )

        return





    # Send voice/audio

    category = context.user_data.get("category")


    if category:


        if text in voices[language][category]["voices"]:


            file_data = voices[language][category]["voices"][text]


            file_id = file_data["id"]
            file_type = file_data["type"]



            caption = f"""
🎙 {text}

📂 {category}

🏛 @Javidan Archive
"""



            try:


                if file_type == "voice":


                    await update.message.reply_voice(
                        voice=file_id,
                        caption=caption
                    )



                elif file_type == "audio":


                    await update.message.reply_audio(
                        audio=file_id,
                        caption=caption
                    )



            except Exception as e:


                print(
                    "SEND ERROR:",
                    e
                )


                await update.message.reply_text(
                    "❌ ارسال فایل با مشکل مواجه شد."
                )






# =========================
# Error Handler
# =========================


async def error_handler(update, context):

    print(
        "ERROR:",
        context.error
    )





# =========================
# Run Bot
# =========================


app = Application.builder().token(TOKEN).build()



app.add_handler(
    CommandHandler(
        "start",
        start
    )
)



app.add_handler(
    CommandHandler(
        "help",
        help_command
    )
)



app.add_handler(
    CommandHandler(
        "about",
        about_command
    )
)



app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    )
)



app.add_error_handler(
    error_handler
)



print("Bot running...")


app.run_polling()
