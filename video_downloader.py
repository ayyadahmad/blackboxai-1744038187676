import os
import requests
import magic
from urllib.parse import urlparse, parse_qs
from pytube import YouTube
from logger import setup_logger
from config import Config

logger = setup_logger(__name__)

class VideoDownloader:
    def __init__(self):
        self.upload_folder = Config.UPLOAD_FOLDER

    def download_video(self, url: str) -> str:
        """
        Download video from various sources and return the local file path
        
        Args:
            url (str): URL of the video to download
            
        Returns:
            str: Local path to the downloaded video file
            
        Raises:
            ValueError: If URL is invalid or video cannot be downloaded
        """
        try:
            # Parse the URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Invalid URL provided")

            # Create unique filename
            filename = f"video_{os.urandom(8).hex()}"
            
            # Handle different types of URLs
            if 'youtube.com' in parsed_url.netloc or 'youtu.be' in parsed_url.netloc:
                return self._download_youtube(url, filename)
            elif 'drive.google.com' in parsed_url.netloc:
                return self._download_gdrive(url, filename)
            else:
                return self._download_direct(url, filename)

        except Exception as e:
            logger.error(f"Error downloading video from {url}: {str(e)}")
            raise ValueError(f"Failed to download video: {str(e)}")

    def _download_youtube(self, url: str, filename: str) -> str:
        """Download video from YouTube"""
        try:
            yt = YouTube(url)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            if not stream:
                raise ValueError("No suitable video stream found")
            
            output_path = os.path.join(self.upload_folder, f"{filename}.mp4")
            stream.download(output_path=self.upload_folder, filename=filename)
            return output_path
            
        except Exception as e:
            logger.error(f"YouTube download error: {str(e)}")
            raise ValueError(f"Failed to download YouTube video: {str(e)}")

    def _download_gdrive(self, url: str, filename: str) -> str:
        """Download video from Google Drive"""
        try:
            # Extract file ID from Google Drive URL
            file_id = None
            if 'id=' in url:
                file_id = parse_qs(parsed_url.query)['id'][0]
            else:
                file_id = url.split('/')[-2]

            download_url = f"https://drive.google.com/uc?id={file_id}"
            
            # Use requests to download the file
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            # Determine file extension using python-magic
            content_type = magic.from_buffer(response.content[:1024], mime=True)
            ext = self._get_extension_from_mime(content_type)
            
            output_path = os.path.join(self.upload_folder, f"{filename}{ext}")
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Google Drive download error: {str(e)}")
            raise ValueError(f"Failed to download from Google Drive: {str(e)}")

    def _download_direct(self, url: str, filename: str) -> str:
        """Download video from direct URL"""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Determine file extension using python-magic
            content_type = magic.from_buffer(response.content[:1024], mime=True)
            ext = self._get_extension_from_mime(content_type)
            
            output_path = os.path.join(self.upload_folder, f"{filename}{ext}")
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Direct download error: {str(e)}")
            raise ValueError(f"Failed to download video: {str(e)}")

    def _get_extension_from_mime(self, mime_type: str) -> str:
        """Get file extension from MIME type"""
        mime_to_ext = {
            'video/mp4': '.mp4',
            'video/quicktime': '.mov',
            'video/x-msvideo': '.avi',
            'video/x-matroska': '.mkv',
            'video/webm': '.webm'
        }
        return mime_to_ext.get(mime_type, '.mp4')  # Default to .mp4 if unknown

    def cleanup(self, filepath: str):
        """Remove downloaded video file"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Cleaned up file: {filepath}")
        except Exception as e:
            logger.error(f"Error cleaning up file {filepath}: {str(e)}")