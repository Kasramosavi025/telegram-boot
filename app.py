from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from telegram import Update
import os
from flask import Flask, request
import cv2
import face_recognition
import numpy as np

# Create Flask app
app = Flask(__name__)

# Bot token
TOKEN = "7614714888:AAEIP9qNVpqJwSlBRlxxKvEPAH7Hsa7sxZA"

# Initialize Updater with the token (no polling)
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

# States for ConversationHandler
CHOOSE_TARGET_FACE, PROCESS_MEDIA = range(2)

# Global variable to store the target face (will be updated dynamically)
target_face = None
target_face_locations = None

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Hello! First, send me the face you want to use for swapping.")
    return CHOOSE_TARGET_FACE

def set_target_face(update: Update, context: CallbackContext) -> int:
    global target_face, target_face_locations
    
    photo = update.message.photo[-1]
    file_id = photo.file_id
    file = context.bot.get_file(file_id)
    file.download('target_face.jpg')
    
    # Load the target face image
    target_face_image = face_recognition.load_image_file("target_face.jpg")
    target_face_locations = face_recognition.face_locations(target_face_image)
    
    if len(target_face_locations) == 0:
        update.message.reply_text("No face detected in the image. Please send another photo with a clear face.")
        return CHOOSE_TARGET_FACE
    
    # Extract the target face
    target_rgb = face_recognition.load_image_file("target_face.jpg")
    target_top, target_right, target_bottom, target_left = target_face_locations[0]
    target_face = target_rgb[target_top:target_bottom, target_left:target_right]
    
    update.message.reply_text("Target face set! Now send a photo or video to swap faces.")
    return PROCESS_MEDIA

def swap_faces(source_image, target_face):
    # Convert image to RGB (face_recognition uses RGB)
    source_rgb = cv2.cvtColor(source_image, cv2.COLOR_BGR2RGB)
    
    # Find all face locations in the source image
    source_face_locations = face_recognition.face_locations(source_rgb)
    
    if len(source_face_locations) == 0:
        return source_image  # No faces found, return original image
    
    # Loop through all detected faces in the source image
    for source_top, source_right, source_bottom, source_left in source_face_locations:
        # Resize the target face to match the size of the source face
        resized_target_face = cv2.resize(target_face, (source_right - source_left, source_bottom - source_top))
        
        # Place the target face onto the source image
        source_rgb[source_top:source_bottom, source_left:source_right] = resized_target_face
    
    # Convert back to BGR for OpenCV
    result_image = cv2.cvtColor(source_rgb, cv2.COLOR_RGB2BGR)
    return result_image

def handle_photo(update: Update, context: CallbackContext) -> int:
    global target_face
    
    if target_face is None:
        update.message.reply_text("Please set a target face first by sending a photo of the face you want to use.")
        return CHOOSE_TARGET_FACE
    
    photo = update.message.photo[-1]
    file_id = photo.file_id
    file = context.bot.get_file(file_id)
    file.download('downloaded_photo.jpg')
    
    # Load the photo with OpenCV
    image = cv2.imread('downloaded_photo.jpg')
    
    # Perform face swap for all faces
    update.message.reply_text("Photo received! Swapping all faces...")
    result_image = swap_faces(image, target_face)
    
    # Save the result
    cv2.imwrite('processed_photo.jpg', result_image)
    update.message.reply_photo(photo=open('processed_photo.jpg', 'rb'))
    
    update.message.reply_text("Send another photo/video to swap faces, or send a new face to change the target face.")
    return PROCESS_MEDIA

def handle_video(update: Update, context: CallbackContext) -> int:
    global target_face
    
    if target_face is None:
        update.message.reply_text("Please set a target face first by sending a photo of the face you want to use.")
        return CHOOSE_TARGET_FACE
    
    video = update.message.video
    file_id = video.file_id
    file = context.bot.get_file(file_id)
    file.download('downloaded_video.mp4')
    
    update.message.reply_text("Video received! Swapping all faces... (This may take a while)")
    
    # Open the video
    cap = cv2.VideoCapture('downloaded_video.mp4')
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('processed_video.mp4', fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Swap all faces in the frame
        processed_frame = swap_faces(frame, target_face)
        out.write(processed_frame)
    
    cap.release()
    out.release()
    
    update.message.reply_video(video=open('processed_video.mp4', 'rb'))
    
    update.message.reply_text("Send another photo/video to swap faces, or send a new face to change the target face.")
    return PROCESS_MEDIA

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Operation cancelled. Send /start to begin again.")
    return ConversationHandler.END

# Set up the conversation handler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        CHOOSE_TARGET_FACE: [MessageHandler(Filters.photo, set_target_face)],
        PROCESS_MEDIA: [
            MessageHandler(Filters.photo, handle_photo),
            MessageHandler(Filters.video, handle_video),
            MessageHandler(Filters.photo, set_target_face)  # Allow setting a new target face
        ],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

# Add the conversation handler to the dispatcher
dispatcher.add_handler(conv_handler)

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
