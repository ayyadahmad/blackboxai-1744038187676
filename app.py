import os
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from video_downloader import VideoDownloader
from content_generator import ContentGenerator
from youtube_api import YouTubeUploader
from whatsapp_handler import WhatsAppHandler
from logger import setup_logger
from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

# Initialize components
logger = setup_logger(__name__)
video_downloader = VideoDownloader()
content_generator = ContentGenerator()
youtube_uploader = YouTubeUploader()
whatsapp_handler = WhatsAppHandler()

@app.route('/')
def index():
    """Render the chat interface"""
    return render_template('chat.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming WhatsApp messages"""
    try:
        # Parse the incoming message
        message_data = whatsapp_handler.parse_incoming_message(request.form)
        if not message_data:
            return jsonify({'status': 'error', 'message': 'Invalid message data'}), 400

        from_number = message_data['from_number']
        message = message_data['message']
        
        # Process the video URL
        process_video.delay(from_number, message)
        
        # Send acknowledgment message
        whatsapp_handler.send_message(
            from_number,
            "🎥 Got your video link! Starting the upload process..."
        )
        
        return jsonify({'status': 'success'}), 200

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/chat/send', methods=['POST'])
def chat_send():
    """Handle messages from the web chat interface"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'status': 'error', 'message': 'Message is required'}), 400

        # Process the video URL
        result = process_video_sync(message)
        
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"Error processing request: {str(e)}"
        }), 500

def process_video_sync(url: str) -> dict:
    """
    Process video synchronously (for web interface)
    Returns progress updates that can be displayed in the UI
    """
    try:
        # Download video
        logger.info(f"Downloading video from: {url}")
        video_path = video_downloader.download_video(url)
        
        # Generate content
        logger.info("Generating video content")
        content = content_generator.generate_content(video_path)
        
        # Upload to YouTube
        logger.info("Uploading to YouTube")
        video_id = youtube_uploader.upload_video(
            video_path,
            content['title'],
            content['description'],
            content['tags']
        )
        
        # Clean up downloaded video
        video_downloader.cleanup(video_path)
        
        # Get video URL
        video_url = youtube_uploader.get_upload_url(video_id)
        
        return {
            'status': 'success',
            'message': 'Video uploaded successfully!',
            'video_url': video_url
        }
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        return {
            'status': 'error',
            'message': f"Failed to process video: {str(e)}"
        }

# For asynchronous processing (WhatsApp messages)
from celery import Celery

# Configure Celery
celery = Celery(
    'youtube_uploader',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

@celery.task
def process_video(from_number: str, url: str):
    """Process video asynchronously and send WhatsApp updates"""
    try:
        # Send starting message
        whatsapp_handler.send_message(
            from_number,
            whatsapp_handler.format_progress_message("downloading")
        )
        
        # Download video
        video_path = video_downloader.download_video(url)
        
        # Update progress
        whatsapp_handler.send_message(
            from_number,
            whatsapp_handler.format_progress_message("generating content")
        )
        
        # Generate content
        content = content_generator.generate_content(video_path)
        
        # Update progress
        whatsapp_handler.send_message(
            from_number,
            whatsapp_handler.format_progress_message("uploading")
        )
        
        # Upload to YouTube
        video_id = youtube_uploader.upload_video(
            video_path,
            content['title'],
            content['description'],
            content['tags']
        )
        
        # Clean up downloaded video
        video_downloader.cleanup(video_path)
        
        # Get video URL and send completion message
        video_url = youtube_uploader.get_upload_url(video_id)
        whatsapp_handler.send_video_complete_message(from_number, video_url)
        
    except Exception as e:
        logger.error(f"Error in async processing: {str(e)}")
        whatsapp_handler.send_error_message(from_number, str(e))

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.YOUTUBE_CREDENTIALS_DIR, exist_ok=True)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=8000)