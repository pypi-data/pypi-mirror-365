import base64
from pyconnector.core.base_google_connector import BaseGoogleAPIConnector


class GmailConnector(BaseGoogleAPIConnector):
    def __init__(self, creds_file=None, token_file='token.pickle', service_account_file=None, scopes: list=None):
        if scopes is None:
            scopes = ['https://www.googleapis.com/auth/gmail.readonly']
        super().__init__(scopes, creds_file, token_file, service_account_file)
        self.service = self.build_service('gmail', 'v1')
    
    def get_profile(self):
        """Get the Gmail profile of the authenticated user."""
        profile = self.service.users().getProfile(userId='me').execute()
        return profile

    def list_labels(self):
        results = self.service.users().labels().list(userId='me').execute()
        return results.get('labels', [])

    def list_messages(self, max_results=10):
        results = self.service.users().messages().list(userId='me', maxResults=max_results).execute()
        return results.get('messages', [])
    
    def get_message(self, message_id):
        message = self.service.users().messages().get(userId='me', id=message_id).execute()
        return message
    
    def get_decoded_message(self, message):
        """Decode the message payload."""
        payload = message.get('payload', {})
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain' and 'data' in part['body']:
                    data = part['body']['data']
                    decoded_data = base64.urlsafe_b64decode(data.encode('UTF-8')).decode('UTF-8')
                    return decoded_data
        elif 'body' in payload and 'data' in payload['body']:
            data = payload['body']['data']
            decoded_data = base64.urlsafe_b64decode(data.encode('UTF-8')).decode('UTF-8')
            return decoded_data 
        return None
    
    def get_attchments(self, message_id, path=None):
        """Get attachments from a message and save them to the specified path."""
        message = self.get_message(message_id)
        attachments = []
        if 'payload' in message and 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if 'filename' in part and part['filename']:
                    if 'body' in part and 'attachmentId' in part['body']:
                        attachment_id = part['body']['attachmentId']
                        attachment = self.service.users().messages().attachments().get(
                            userId='me', messageId=message_id, id=attachment_id).execute()
                        data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                        if path:
                            with open(f"{path}/{part['filename']}", 'wb') as f:
                                f.write(data)
                        attachments.append({'filename': part['filename'], 'data': data})
        return attachments
    
    def get_inline_images(self, message_id, path=None):
        """Get inline images from a message and save them to the specified path."""
        message = self.get_message(message_id)
        inline_images = []
        if 'payload' in message and 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part.get('mimeType', '').startswith('image/') and 'body' in part and 'data' in part['body']:
                    data = base64.urlsafe_b64decode(part['body']['data'].encode('UTF-8'))
                    if path:
                        with open(f"{path}/{part['filename']}", 'wb') as f:
                            f.write(data)
                    inline_images.append({'filename': part['filename'], 'data': data})
        return inline_images

    def send_message(self, message):
        """Send a message using the Gmail API."""
        message = self.service.users().messages().send(userId='me', body=message).execute()
        return message

    def delete_message(self, message_id):
        """Delete a message by ID."""
        self.service.users().messages().delete(userId='me', id=message_id).execute()
        return f'Message with ID {message_id} deleted successfully.'
    
    