from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
TOKEN = "7614714888:AAEIP9qNVpqJwSlBRlxxKvEPAH7Hsa7sxZA"

def start(update, context):
    update.message.reply_text("Hello! Send me a video or photo, and I'll process it.")

def handle_video(update, context):
    video = update.message.video
    file_id = video.file_id
    file = context.bot.get_file(file_id)
    file.download('downloaded_video.mp4')
    update.message.reply_text("Video received! Processing... (For now, I'll just send it back)")
    update.message.reply_video(video=open('downloaded_video.mp4', 'rb'))

def handle_photo(update, context):
    photo = update.message.photo[-1]
    file_id = photo.file_id
    file = context.bot.get_file(file_id)
    file.download('downloaded_photo.jpg')
    update.message.reply_text("Photo received! Processing... (For now, I'll just send it back)")
    update.message.reply_photo(photo=open('downloaded_photo.jpg', 'rb'))

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.video, handle_video))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
