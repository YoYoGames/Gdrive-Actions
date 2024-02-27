import os
import logging
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import json
import io

def error(message):
    logging.error(message)

def debug(message):
    logging.debug(message)

def main(action, filename, name, drive_id, folder_id, credentials_file_secret, encoded, overwrite):
    try:
        # Retrieve encoded credentials file path from secret
        encoded_credentials_file_path = os.getenv(credentials_file_secret)

        if encoded_credentials_file_path is None:
            raise ValueError("Encoded credentials file path not found in secrets.")

        # Decode the credentials file path
        credentials_file_path = base64.b64decode(encoded_credentials_file_path).decode('utf-8')

        # Ensure that the credentials file exists
        if not os.path.isfile(credentials_file_path):
            raise FileNotFoundError(f"Credentials file '{credentials_file_path}' not found.")

        # Fetching a JWT config with credentials and the right scope
        with open(credentials_file_path, 'r') as file:
            credentials = json.load(file)
            creds = service_account.Credentials.from_service_account_info(credentials, scopes=["https://www.googleapis.com/auth/drive.file"])

        # Instantiate a new Drive service
        service = build('drive', 'v3', credentials=creds)

        if action == 'download':
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

    except ValueError as e:
        error(f"Error: {e}")
    except FileNotFoundError as e:
        error(f"Error: {e}")
    except Exception as e:
        error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Configure logging to output debug messages
    logging.basicConfig(level=logging.DEBUG)

    # Fetch environment variables
    action = os.getenv('INPUT_ACTION')
    filename = os.getenv('INPUT_FILENAME')
    name = os.getenv('INPUT_NAME')
    drive_id = os.getenv('INPUT_DRIVE_ID')
    folder_id = os.getenv('INPUT_FOLDER_ID')
    credentials_file_secret = 'INPUT_CREDENTIALS_FILE'  # Adjust this to match your secret name
    encoded = os.getenv('INPUT_ENCODED')
    overwrite = os.getenv('INPUT_OVERWRITE')

    # Perform type conversion where necessary
    encoded = encoded.lower() == 'true' if encoded else True  # Convert to boolean
    overwrite = overwrite.lower() == 'true' if overwrite else False  # Convert to boolean

    # Call the main function
    main(action, filename, name, drive_id, folder_id, credentials_file_secret, encoded, overwrite)
