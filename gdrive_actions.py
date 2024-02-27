import base64
import os
import logging
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import argparse
import json
from google.auth.transport.requests import Request as AuthRequest
import socket
import io

def main(action, filename, name, drive_id, folder_id, credentials_file, encoded, overwrite):
    # Ensure that the credentials file exists
    if not os.path.isfile(credentials_file):
        error(f"Credentials file '{credentials_file}' not found.")
        return

    # Read the base64-encoded credentials from the file
    with open(credentials_file, 'r') as file:
        credentials_base64 = file.read()

    try:
        # Decode the base64 string
        credentials_json = base64.b64decode(credentials_base64).decode('utf-8')

        # Parse the decoded JSON string to obtain the credentials
        credentials = json.loads(credentials_json)
    except Exception as e:
        error(f"Error decoding/parsing credentials: {e}")
        return

    # Fetching a JWT config with credentials and the right scope
    try:
        creds = service_account.Credentials.from_service_account_info(credentials, scopes=["https://www.googleapis.com/auth/drive.file"])
    except Exception as e:
        error(f"Fetching JWT credentials failed with error: {e}")
        return

    # Instantiate a new Drive service
    try:
        service = build('drive', 'v3', credentials=creds)
    except Exception as e:
        error(f"Instantiating Google Drive service failed with error: {e}")
        return

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
        # create drive api client
            service = build('drive', 'v3', credentials=creds)

            drive_id = folder_id

        # pylint: disable=maybe-no-member
            request = service.files().get_media(fileId=folder_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(F'Download {int(status.progress() * 100)}.')

        # Save the downloaded file to a local file
            download_path = filename  # Specify the path where you want to save the file
            with open(download_path, 'wb') as f:
                f.write(file.getvalue())
            print(F'Download completed. File saved to {download_path}')

        except HttpError as error:
            print(F'An error occurred: {error}')

def error(message):
    logging.error(message)

def debug(message):
    logging.debug(message)


if __name__ == "__main__":

    # Configure logging to output debug messages
    logging.basicConfig(level=logging.DEBUG)

    # Set socket timeout to None to prevent timeout
    socket.setdefaulttimeout(None)    
    parser = argparse.ArgumentParser(description='Upload or Download file from Google Drive')
    parser.add_argument('--action', choices=['upload', 'download'], help='Action to perform: upload or download')
    parser.add_argument('--filename', type=str, help='Path to the file to upload')
    parser.add_argument('--name', type=str, help='Name of the file on Google Drive')
    parser.add_argument('--drive_id', type=str, help='ID of the folder on Google Drive to upload the file to')
    parser.add_argument('--folder_id', type=str, help='ID of the file on Gdrive to download (for download action)')
    parser.add_argument('--credentials_file', type=str, help='Base64 encoded Google service account credentials')
    parser.add_argument('--encoded', type=str, help='Boolean indicating whether credentials are base64 encoded', default='true')
    parser.add_argument('--overwrite', type=str, help='Boolean indicating whether to overwrite existing files', default='false')

    args = parser.parse_args()

    main(args.action, args.filename, args.name, args.folder_id, args.drive_id, args.credentials_file, args.encoded, args.overwrite)
