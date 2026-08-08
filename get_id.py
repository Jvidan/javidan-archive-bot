from telegram.ext import Application, MessageHandler, filters


async def get_id(update, context):

    if update.message.voice:

        print("TYPE: voice")
        print(update.message.voice.file_id)


    elif update.message.audio:

        print("TYPE: audio")
        print(update.message.audio.file_id)



app = Application.builder().token(TOKEN).build()


app.add_handler(
    MessageHandler(
        filters.VOICE | filters.AUDIO,
        get_id
    )
)


print("Listening...")

app.run_polling()
