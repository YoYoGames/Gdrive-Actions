import os
import logging
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import json
import socket
import io
import base64

def error(message):
    logging.error(message)

def debug(message):
    logging.debug(message)

def main(action, filename, name, drive_id, folder_id, credentials_file):
        # Retrieve encoded credentials content from secret
        encoded_credentials_content = os.getenv(credentials_file)

        # if encoded_credentials_content is None:
        #     raise ValueError("Encoded credentials content not found in secrets.")

        # Decode the credentials content
        credentials_base64 = encoded_credentials_content.encode('utf-8')
        credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
        credentials = json.loads(credentials_json)

        # Fetching a JWT config with credentials and the right scope
        creds = service_account.Credentials.from_service_account_info(credentials, scopes=["https://www.googleapis.com/auth/drive.file"])

        # Instantiate a new Drive service
        service = build('drive', 'v3', credentials=creds)

        if action == 'upload':
            try:
                file_metadata = {'name': name, 'parents': [drive_id]}
                media = MediaFileUpload(filename, mimetype='application/zip', resumable=True)

                # Perform the upload
                response = service.files().create(
                    body=file_metadata,
                    media_body=media,
                    supportsAllDrives=True,
                    fields='id'
                ).execute()

                # Log the upload completion
                debug(f"Upload completed. File ID: {response.get('id')}")

            except Exception as e:
                error(f"An unexpected error occurred: {e}")
             
        elif action == 'download':
            try:
                request = service.files().get_media(fileId=folder_id)
                file = io.BytesIO()
                downloader = MediaIoBaseDownload(file, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print(f'Download {int(status.progress() * 100)}.')

                # Save the downloaded file to a local file
                download_path = filename  # Specify the path where you want to save the file
                with open(download_path, 'wb') as f:
                    f.write(file.getvalue())
                print(f'Download completed. File saved to {download_path}')

            except HttpError as error:
                print(f'An error occurred: {error}')
        

if __name__ == "__main__":
    # Configure logging to output debug messages
    logging.basicConfig(level=logging.DEBUG)

    # Set socket timeout to None to prevent timeout
    socket.setdefaulttimeout(None)    

    # Fetch environment variables
    action = os.getenv('INPUT_ACTION')
    filename = os.getenv('INPUT_FILENAME')
    name = os.getenv('INPUT_NAME')
    drive_id = os.getenv('INPUT_DRIVE_ID')
    folder_id = os.getenv('INPUT_FOLDER_ID')
    credentials_file = os.getenv('INPUT_CREDENTIALS_FILE')
    # encoded = os.getenv('INPUT_ENCODED')
    overwrite = os.getenv('INPUT_OVERWRITE')

    # # Perform type conversion where necessary
    # encoded = encoded.lower() == 'true' if encoded else True  # Convert to boolean
    # overwrite = overwrite.lower() == 'true' if overwrite else False  # Convert to boolean

    # Call the main function
    main(action, filename, name, drive_id, folder_id, credentials_file)
