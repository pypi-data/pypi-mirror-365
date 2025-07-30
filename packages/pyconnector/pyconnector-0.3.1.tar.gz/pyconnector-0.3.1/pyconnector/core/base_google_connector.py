import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class BaseGoogleAPIConnector:
    def __str__(self):
        return """
        Initialize authentication for Google API.

            Args:
                scopes (list(str)): List of scopes required for the API.
                creds_file (str): Path to OAuth client secrets JSON file (for user OAuth flow).
                token_file (str): Path to token pickle file to cache OAuth tokens.
                service_account_file (str): Path to service account JSON key file.
        """

    def __init__(self, scopes, creds_file=None, token_file='token.pickle', service_account_file=None):
        self.creds = None
        self.scopes = scopes
        self.creds_file = creds_file
        self.token_file = token_file
        self.service_account_file = service_account_file
        self.service = None

        self._authenticate()

    def _authenticate(self):
        """Handles authentication via service account or OAuth user flow."""
        if self.service_account_file:
            # Use service account credentials (no user interaction)
            self.creds = service_account.Credentials.from_service_account_file(
                self.service_account_file, scopes=self.scopes)
        else:
            # OAuth user flow with cached token
            if os.path.exists(self.token_file):
                self.creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)

            # If no valid creds, run OAuth flow
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not self.creds_file:
                        raise ValueError("creds_file must be provided for OAuth flow")
                    flow = InstalledAppFlow.from_client_secrets_file(self.creds_file, self.scopes)
                    self.creds = flow.run_local_server(port=8080)
                # Save token for next time
                with open(self.token_file, 'w') as token:
                    token.write(self.creds.to_json())

    def build_service(self, api_name, api_version):
        """
        Build and return the Google API service client.

        Args:
            api_name (str): Google API name, e.g., 'gmail', 'drive'.
            api_version (str): API version, e.g., 'v1', 'v3'.

        Returns:
            googleapiclient.discovery.Resource: The service client.
        """
        if not self.creds:
            raise Exception("Authentication credentials not found.")
        self.service = build(api_name, api_version, credentials=self.creds)
        return self.service
    
    
