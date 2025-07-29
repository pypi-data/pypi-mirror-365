import os
from pyconnector.core.base_google_connector import BaseGoogleAPIConnector
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

class DriveConnector(BaseGoogleAPIConnector):
    def __init__(self, creds_file=None, token_file='token.pickle', service_account_file=None, scopes: list=None):
        if scopes is None:
            scopes = ['https://www.googleapis.com/auth/drive']
        super().__init__(scopes, creds_file, token_file, service_account_file)
        self.service = self.build_service('drive', 'v3')

    def get_profile(self):
        """Get Google Drive user profile info (basic user and storage quota)."""
        profile = self.service.about().get(fields="user(displayName, emailAddress, photoLink, permissionId), storageQuota").execute()
        return profile

    def list_files(self, page_size=10):
        """List files in the root folder (no folders or files filter)."""
        results = self.service.files().list(
            pageSize=page_size,
            fields="files(id, name, mimeType, parents)"
        ).execute()
        return results.get('files', [])

    def list_folder_tree(self, folder_id='root', indent=0):
        """
        Recursively list files and folders in a tree starting at folder_id.
        Prints the tree structure with indentation.
        """
        query = f"'{folder_id}' in parents and trashed = false"
        results = self.service.files().list(
            q=query,
            fields="files(id, name, mimeType)"
        ).execute()
        items = results.get('files', [])

        for item in items:
            prefix = '│   ' * indent + '├── '
            print(f"{prefix}{item['name']} [{'Folder' if item['mimeType'] == 'application/vnd.google-apps.folder' else 'File'}]")

            if item['mimeType'] == 'application/vnd.google-apps.folder':
                # Recursive call for subfolders
                self.list_folder_tree(item['id'], indent=indent+1)

    def upload_file(self, file_path, mime_type, folder_id=None):
        """
        Upload a single file to Drive. If folder_id is specified, upload inside that folder.
        """
        file_metadata = {'name': os.path.basename(file_path)}
        if folder_id:
            file_metadata['parents'] = [folder_id]
        media = MediaFileUpload(file_path, mimetype=mime_type)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')

    def upload_folder(self, local_folder_path, parent_drive_folder_id='root'):
        """
        Recursively upload the contents of a local folder and subfolders to Drive inside the given parent_drive_folder_id.
        Returns the Google Drive folder ID created/used.
        """
        folder_name = os.path.basename(local_folder_path.rstrip('/\\'))
        # Create folder on Drive
        metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_drive_folder_id] if parent_drive_folder_id else []
        }
        folder = self.service.files().create(body=metadata, fields='id').execute()
        folder_id = folder['id']

        for entry in os.listdir(local_folder_path):
            full_path = os.path.join(local_folder_path, entry)
            if os.path.isdir(full_path):
                # Recursive upload for subfolders
                self.upload_folder(full_path, parent_drive_folder_id=folder_id)
            else:
                mime_type = self._get_mime_type(full_path)
                self.upload_file(full_path, mime_type, folder_id)

        return folder_id

    def download_file(self, file_id, save_path):
        """
        Download a single file from Drive by file_id to save_path (directory with filename).
        """
        request = self.service.files().get_media(fileId=file_id)
        fh = io.FileIO(save_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        try:
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%.")
        except Exception as e:
            print(f"Error downloading file: {e}")
        fh.close()
        print(f"File saved to {save_path}")

    def download_files(self, file_ids, save_dir):
        """
        Download multiple files given their IDs into the specified directory.
        """
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        for fid in file_ids:
            # Get file metadata to find filename
            metadata = self.service.files().get(fileId=fid, fields='name').execute()
            filepath = os.path.join(save_dir, metadata['name'])
            self.download_file(fid, filepath)

    def _get_mime_type(self, filepath):
        """
        Helper: Guess MIME type of file based on extension.
        You can improve this by importing python-magic or similar if you want accurate detection.
        """
        import mimetypes
        mime_type, _ = mimetypes.guess_type(filepath)
        return mime_type or 'application/octet-stream'