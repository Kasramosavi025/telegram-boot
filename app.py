from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update
import os
from flask import Flask, request

# Create Flask app
app = Flask(__name__)

# Bot token
TOKEN = "7614714888:AAEIP9qNVpqJwSlBRlxxKvEPAH7Hsa7sxZA"

# Initialize Updater with the token (no polling)
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Define handlers
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! Send me a video or photo, and I'll process it.")

def handle_video(update: Update, context: CallbackContext):
    video = update.message.video
    file_id = video.file_id
    file = context.bot.get_file(file_id)
    file.download('downloaded_video.mp4')
    update.message.reply_text("Video received! Processing... (For now, I'll just send it back)")
    update.message.reply_video(video=open('downloaded_video.mp4', 'rb'))

def handle_photo(update: Update, context: CallbackContext):
    photo = update.message.photo[-1]
    file_id = photo.file_id
    file = context.bot.get_file(file_id)
    file.download('downloaded_photo.jpg')
    update.message.reply_text("Photo received! Processing... (For now, I'll just send it back)")
    update.message.reply_photo(photo=open('downloaded_photo.jpg', 'rb'))

# Add handlers to dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.video, handle_video))
dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo))

# Flask route to handle Telegram updates
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), updater.bot)
    dispatcher.process_update(update)
    return 'OK', 200

# Set webhook on startup
@app.route('/')
def set_webhook():
    webhook_url = f"https://my-telegram-boot.onrender.com/{TOKEN}"
    updater.bot.set_webhook(webhook_url)
    return "Webhook set!", 200

if __name__ == '__main__':
    # Run Flask app on the port specified by Render (default is 10000)
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
