from pathlib import Path
from urllib.parse import urljoin

import markdown
import requests
from prettyconf import config

from . import settings, utils


class ApiClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config('BREVO_API_KEY')
        self.base_url = settings.BREVO_API_BASE_URL

    def send_email(
        self,
        to: str,
        subject: str,
        content: str,
        content_type: str = 'txt',
        sender_email: str = None,
        sender_name: str = None,
        attachments: list[str | Path] | str | Path = None,
    ) -> dict:
        """Send an email using the Brevo API.
        Args:
            to (str): Recipient email address.
            subject (str): Subject of the email.
            content (str): Content of the email.
            content_type (str): Type of content: 'txt' for text (default), 'md' for markdown, 'html' for HTML.
            sender_email (str): Sender's email address (optional, uses default if not provided).
            sender_name (str): Sender's name (optional, uses default if not provided).
            attachments (list | str | Path): List of file paths to attach to the email (optional).
        Returns:
            dict: Response from the Brevo API.

        API details: https://developers.brevo.com/reference/sendtransacemail
        """
        API_PATH = 'smtp/email'
        url = urljoin(self.base_url, API_PATH)
        sender_email = sender_email or config(
            'BREVO_SENDER_EMAIL', default=settings.BREVO_SENDER_EMAIL
        )
        sender_name = sender_name or config('BREVO_SENDER_NAME', default=settings.BREVO_SENDER_NAME)
        headers = {'api-key': self.api_key, 'Content-Type': 'application/json'}
        data = {
            'sender': {'email': sender_email, 'name': sender_name},
            'to': [{'email': to}],
            'subject': subject,
        }
        # Handle content based on type
        match content_type.lower():
            case 'txt':
                data['textContent'] = content
            case 'md':
                markdown_content = markdown.markdown(content)
                data['htmlContent'] = markdown_content
            case 'html':
                data['htmlContent'] = content
            case _:
                raise ValueError("Invalid content type. Use 'txt', 'md', or 'html'.")
        # Handle attachments
        if attachments:
            if not isinstance(attachments, list):
                attachments = [attachments]
            data['attachment'] = [
                {'name': Path(file).name, 'content': utils.encode_file_to_base64(file)}
                for file in attachments
            ]
        response = requests.post(url, headers=headers, json=data)
        return response.json()
