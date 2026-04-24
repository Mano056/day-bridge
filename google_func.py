from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
import base64

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def service_gmail():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TOKEN_PATH = os.path.join(BASE_DIR, "token.json")
    CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is 
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    service =  build("gmail", "v1", credentials=creds)
    return service

def read_emails(service, max_results=5):
    try:
        results = service.users().messages().list(userId="me", maxResults=max_results).execute()
        message_refs = results.get("messages", [])
    except HttpError as e:
        print(f"An error occured: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

    if not message_refs:
        return []
    
    message_list = []
        
    for message_ref in message_refs:
        message_id = message_ref.get("id")
        if not message_id:
            continue

        try:
            message = service.users().messages().get(userId="me", id=message_id).execute()
            headers = message.get("payload", {}).get("headers", [])

            sender = "Unknown sender"
            subject = "No subject"

            for header in headers:
                if header.get("name") == "From":
                    sender = header.get("value", sender)
                elif header.get("name") == "Subject":
                    subject = header.get("value", subject)

            snippet = message.get("snippet", "")
            message_list.append({
                "Sender": sender,
                "Subject": subject,
                "Snippet": snippet
            })
        except HttpError as e:
            print(f"An error occurred for message {message_id}: {e}")
        except Exception as e:
            print(f"Unexpected error on {message_id}: {e}")
        
    return message_list
        
def send_email(service, to, subject, body):
    try:
        message = MIMEText(body)
        message["To"] = to
        message["Subject"] = subject
        
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": encoded_message}

        sent_message = service.users().messages().send(
            userId="me", 
            body=create_message
            ).execute()
        
        return {
            "success": True,
            "id": sent_message.get("id")
        }

    except HttpError as error:
        print(f"An error occurred while sending: {error}")
        return{
            "success": False,
            "error": str(error)
        }