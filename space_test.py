from json import dumps
from httplib2 import Http
# Copy the webhook URL from the Chat space where the webhook is registered.
# The values for SPACE_ID, KEY, and TOKEN are set by Chat, and are included
# when you copy the webhook URL.


# def main():
#     """Google Chat incoming webhook quickstart."""
#     url = "https://chat.googleapis.com/v1/spaces/AAAA2QVj5BU/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=mMa2upQ6zjPvOGoh-AsxArlnT93lRqn2N6U-9FE9OgQ"
#     app_message = {"text": "Hello from a Python script! @21f1000506"}
#     message_headers = {"Content-Type": "application/json; charset=UTF-8"}
#     http_obj = Http()
#     response = http_obj.request(
#         uri=url,
#         method="POST",
#         headers=message_headers,
#         body=dumps(app_message),
#     )
#     print(response)
#
#
# if __name__ == "__main__":
#     main()

# from googleapiclient.discovery import build
# from google.oauth2.service_account import Credentials
#
# # Replace with your downloaded JSON key file path
# credentials = Credentials.from_service_account_file('space_creds.json')
#
# service = build('chat', 'v1', credentials=credentials)
#
# # Replace with the Space ID
# space_id = 'AAAA2QVj5BU'
#
# # Message content with user mention (replace with '@username')
# message_body = "This message mentions @21f1000506"
#
# # Build the message object
# message = {
#     'text': message_body
# }
#
# # Send the message to the Space
# try:
#     response = service.spaces().messages().create(
#         body=message, parent=f'spaces/{space_id}').execute()
#     print(f'Message sent successfully. Response: {response}')
# except Exception as e:
#     print(f'Error sending message: {e}')
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Path to your service account key file
SERVICE_ACCOUNT_FILE = 'space_creds.json'

# Scopes required for Google Chat API
SCOPES = ['https://www.googleapis.com/auth/chat.bot']

# Authenticate using the service account
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the Google Chat API service
service = build('chat', 'v1', credentials=credentials)

# Details for the new space
space_body = {
    'name': 'paradox/godavari',
    'displayName': 'Paradox Godavari',
    'spaceType': 'SPACE'  # Use 'SPACE' for standard spaces or 'GROUP_CHAT' for direct messages
}

# Create the new space
response = service.spaces().create(body=space_body).execute()

print('Space created: {}'.format(response))
