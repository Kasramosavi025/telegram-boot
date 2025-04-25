۲۰۲۵/۴/۲۵   ۰۹:۴۳

app.py

from flask import Flask, request
import telebot
import cv2
import numpy as np
import os

app = Flask(__name__)

TOKEN = '7219454468:AAF-V-NBEJzVuQ2beymQzv3Qs3victq-PjA'
bot = telebot.TeleBot(TOKEN)

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_json())
    bot.process_new_updates([update])
    return 'OK', 200

@bot.message_handler(content_types=['video'])
def handle_video(message):
    bot.reply_to(message, "Please wait, processing video...")
    file_info = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('input_video.mp4', 'wb') as f:
        f.write(downloaded_file)
    bot.reply_to(message, "Video received. Now send a photo of the face to swap.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('target_face.jpg', 'wb') as f:
        f.write(downloaded_file)
    bot.reply_to(message, "Photo received. Processing face swap...")

    # Load target face
    target_face_img = cv2.imread('target_face.jpg')
    if target_face_img is None:
        bot.reply_to(message, "Failed to load the photo!")
        return

    # Process video (simple placeholder for face swap)
    cap = cv2.VideoCapture('input_video.mp4')
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output_video.mp4', fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # Placeholder: Just copy the frame for now
        out.write(frame)
    
    cap.release()
    out.release()
    
    with open('output_video.mp4', 'rb') as video:
        bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id)
    bot.reply_to(message, "Video processing done! Face swap will be added soon.")

if __name__ == '__main__':
    bot.remove_webhook()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)