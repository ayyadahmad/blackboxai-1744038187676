from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from logger import setup_logger
from config import Config

logger = setup_logger(__name__)

class WhatsAppHandler:
    def __init__(self):
        self.client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        self.whatsapp_number = Config.TWILIO_PHONE_NUMBER

    def send_message(self, to_number: str, message: str) -> bool:
        """
        Send a WhatsApp message using Twilio
        
        Args:
            to_number (str): Recipient's phone number (with country code)
            message (str): Message to send
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            # Ensure the number is in WhatsApp format
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'

            # Format the from number
            from_number = f'whatsapp:{self.whatsapp_number}'

            # Send the message
            message = self.client.messages.create(
                body=message,
                from_=from_number,
                to=to_number
            )

            logger.info(f"Message sent successfully. SID: {message.sid}")
            return True

        except TwilioRestException as e:
            logger.error(f"Twilio error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return False

    def parse_incoming_message(self, request_data: dict) -> dict:
        """
        Parse incoming WhatsApp message from Twilio webhook
        
        Args:
            request_data (dict): The webhook request data from Twilio
            
        Returns:
            dict: Parsed message data containing:
                - from_number (str): Sender's phone number
                - message (str): Message content
                - media_url (str, optional): URL of any attached media
        """
        try:
            result = {
                'from_number': request_data.get('From', '').replace('whatsapp:', ''),
                'message': request_data.get('Body', ''),
                'media_url': None
            }

            # Check for media attachments
            num_media = int(request_data.get('NumMedia', 0))
            if num_media > 0:
                result['media_url'] = request_data.get('MediaUrl0')

            return result

        except Exception as e:
            logger.error(f"Error parsing incoming message: {str(e)}")
            return None

    def format_progress_message(self, stage: str, progress: int = None, error: str = None) -> str:
        """
        Format a progress update message
        
        Args:
            stage (str): Current processing stage
            progress (int, optional): Progress percentage
            error (str, optional): Error message if any
            
        Returns:
            str: Formatted message
        """
        if error:
            return f"❌ Error during {stage}: {error}"

        status_emojis = {
            'downloading': '⬇️',
            'processing': '⚙️',
            'generating': '✍️',
            'uploading': '⬆️',
            'complete': '✅'
        }

        emoji = status_emojis.get(stage.lower(), '📝')
        
        if progress is not None:
            progress_bar = self._generate_progress_bar(progress)
            return f"{emoji} {stage.capitalize()}: {progress}%\n{progress_bar}"
        
        return f"{emoji} {stage.capitalize()}..."

    def _generate_progress_bar(self, progress: int, length: int = 10) -> str:
        """Generate a text-based progress bar"""
        filled = int(length * progress / 100)
        bar = '█' * filled + '░' * (length - filled)
        return f"[{bar}]"

    def send_video_complete_message(self, to_number: str, video_url: str) -> bool:
        """
        Send a completion message with the YouTube video link
        
        Args:
            to_number (str): Recipient's phone number
            video_url (str): YouTube video URL
            
        Returns:
            bool: True if message was sent successfully
        """
        message = (
            "✅ Video Upload Complete!\n\n"
            f"🎥 Watch your video here:\n{video_url}\n\n"
            "👉 The video is currently set as private. "
            "You can change its privacy settings in YouTube Studio."
        )
        
        return self.send_message(to_number, message)

    def send_error_message(self, to_number: str, error: str) -> bool:
        """
        Send an error message
        
        Args:
            to_number (str): Recipient's phone number
            error (str): Error message
            
        Returns:
            bool: True if message was sent successfully
        """
        message = (
            "❌ Error Processing Video\n\n"
            f"Details: {error}\n\n"
            "Please try again or contact support if the issue persists."
        )
        
        return self.send_message(to_number, message)