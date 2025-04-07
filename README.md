# YouTube Video Upload Assistant

A powerful tool that automates the process of uploading videos to YouTube. Share a video link (Google Drive or direct URL) via WhatsApp or web interface, and the assistant will:

✨ Download the video  
✨ Generate an engaging title  
✨ Create a detailed description  
✨ Add relevant tags and hashtags  
✨ Upload the video directly to YouTube  

## Features

- **Multi-platform Support**: Upload videos from various sources including Google Drive and direct URLs
- **Automated Content Generation**: Automatically generates titles, descriptions, and tags
- **Dual Interface**: 
  - WhatsApp integration for mobile convenience
  - Modern web interface for desktop users
- **Progress Tracking**: Real-time updates on upload progress
- **Error Handling**: Robust error handling with user-friendly notifications
- **Secure**: Uses OAuth 2.0 for YouTube authentication

## Prerequisites

- Python 3.8 or higher
- Redis server (for Celery task queue)
- YouTube API credentials
- Twilio account (for WhatsApp integration)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/youtube-upload-assistant.git
cd youtube-upload-assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with the following:
```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True

# YouTube API Configuration
YOUTUBE_CLIENT_SECRETS_FILE=path/to/your/client_secrets.json

# Twilio (WhatsApp) Configuration
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=your-twilio-whatsapp-number
```

5. Set up YouTube API:
- Go to the [Google Cloud Console](https://console.cloud.google.com)
- Create a new project
- Enable the YouTube Data API v3
- Create OAuth 2.0 credentials
- Download the client secrets file and save it as specified in your .env file

## Running the Application

1. Start the Redis server:
```bash
redis-server
```

2. Start the Celery worker:
```bash
celery -A app.celery worker --loglevel=info
```

3. Run the Flask application:
```bash
python app.py
```

The application will be available at `http://localhost:8000`

## Usage

### Via Web Interface

1. Open your browser and navigate to `http://localhost:8000`
2. Paste your video link in the chat input
3. Click Send or press Enter
4. Wait for the upload process to complete
5. You'll receive the YouTube video link once the upload is finished

### Via WhatsApp

1. Send a message to your configured WhatsApp number
2. Share the video link
3. Wait for progress updates
4. Receive the YouTube video link once complete

## Project Structure

```
youtube-upload-assistant/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── youtube_api.py        # YouTube API integration
├── video_downloader.py   # Video download functionality
├── content_generator.py  # Content generation logic
├── whatsapp_handler.py   # WhatsApp integration
├── logger.py            # Logging configuration
├── requirements.txt     # Python dependencies
├── templates/           # HTML templates
│   ├── base.html       # Base template
│   └── chat.html       # Chat interface
└── logs/               # Log files
```

## Error Handling

The application includes comprehensive error handling for:
- Invalid video URLs
- Download failures
- YouTube API issues
- Network connectivity problems
- Authentication errors

All errors are logged and user-friendly error messages are displayed.

## Security Considerations

- All sensitive credentials are stored in environment variables
- YouTube authentication uses OAuth 2.0
- File uploads are validated and sanitized
- Temporary files are automatically cleaned up
- HTTPS is recommended for production deployment

## Production Deployment

For production deployment:

1. Use a production-grade WSGI server (e.g., Gunicorn):
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

2. Set up HTTPS using a reverse proxy (e.g., Nginx)

3. Configure proper security headers

4. Use environment-specific configuration

5. Set up monitoring and logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.