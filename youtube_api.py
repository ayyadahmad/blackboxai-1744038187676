import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from logger import setup_logger
from config import Config

logger = setup_logger(__name__)

class YouTubeUploader:
    def __init__(self):
        self.credentials_dir = Config.YOUTUBE_CREDENTIALS_DIR
        self.client_secrets_file = Config.YOUTUBE_CLIENT_SECRETS_FILE
        self.scopes = Config.YOUTUBE_API_SCOPES
        self.credentials = None
        self.youtube = None

    def authenticate(self):
        """Authenticate with YouTube API using OAuth 2.0"""
        try:
            # Token file path
            token_file = os.path.join(self.credentials_dir, 'token.pickle')

            # Check if we have valid credentials
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    self.credentials = pickle.load(token)

            # If credentials are invalid or don't exist, get new ones
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    logger.info("Refreshing YouTube API credentials")
                    self.credentials.refresh(Request())
                else:
                    logger.info("Getting new YouTube API credentials")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.client_secrets_file, self.scopes)
                    self.credentials = flow.run_local_server(port=0)

                # Save credentials for future use
                with open(token_file, 'wb') as token:
                    pickle.dump(self.credentials, token)

            # Build YouTube API service
            self.youtube = build('youtube', 'v3', credentials=self.credentials)
            logger.info("Successfully authenticated with YouTube API")
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise ValueError(f"Failed to authenticate with YouTube: {str(e)}")

    def upload_video(self, video_path: str, title: str, description: str, tags: list) -> str:
        """
        Upload video to YouTube
        
        Args:
            video_path (str): Path to the video file
            title (str): Video title
            description (str): Video description
            tags (list): List of tags
            
        Returns:
            str: YouTube video ID
            
        Raises:
            ValueError: If upload fails
        """
        try:
            if not self.youtube:
                self.authenticate()

            # Prepare the video upload request
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'categoryId': '22'  # Category 22 is "People & Blogs"
                },
                'status': {
                    'privacyStatus': 'private',  # Upload as private initially
                    'selfDeclaredMadeForKids': False
                }
            }

            # Create MediaFileUpload object
            media = MediaFileUpload(
                video_path,
                chunksize=1024*1024,  # 1MB chunks
                resumable=True
            )

            # Create the video insert request
            logger.info(f"Starting upload for video: {title}")
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )

            # Upload the video
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.info(f"Upload progress: {progress}%")

            logger.info(f"Upload complete! Video ID: {response['id']}")
            return response['id']

        except HttpError as e:
            error_message = f"HTTP error occurred: {e.resp.status} {e.content}"
            logger.error(error_message)
            raise ValueError(error_message)
        except Exception as e:
            error_message = f"Error uploading video: {str(e)}"
            logger.error(error_message)
            raise ValueError(error_message)

    def update_video_privacy(self, video_id: str, privacy_status: str = 'public'):
        """
        Update the privacy status of a video
        
        Args:
            video_id (str): YouTube video ID
            privacy_status (str): Privacy status ('private', 'unlisted', or 'public')
        """
        try:
            if not self.youtube:
                self.authenticate()

            self.youtube.videos().update(
                part='status',
                body={
                    'id': video_id,
                    'status': {
                        'privacyStatus': privacy_status
                    }
                }
            ).execute()
            
            logger.info(f"Updated video {video_id} privacy to {privacy_status}")
            
        except Exception as e:
            logger.error(f"Error updating video privacy: {str(e)}")
            raise ValueError(f"Failed to update video privacy: {str(e)}")

    def get_upload_url(self, video_id: str) -> str:
        """Get the URL of the uploaded video"""
        return f"https://www.youtube.com/watch?v={video_id}"