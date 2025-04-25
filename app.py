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
    update.message.reply_video(video=open('down
