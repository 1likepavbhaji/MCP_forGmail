import os
from mcp.server.fastmcp import FastMCP
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.message import EmailMessage
import logging

app = FastMCP("mail_server")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(SCRIPT_DIR, "credentials.json")
TOKEN_PATH = os.path.join(SCRIPT_DIR, "token.json")
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send"
]
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Gmail MCP server started")

#Token Authentication
def get_gmail_service():
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

#An overview of mails received

@app.tool()
def prof_overview():
    auth_client=get_gmail_service()
    profile = auth_client.users().getProfile(userId="me").execute()
    email = profile["emailAddress"]
    total_messages = profile["messagesTotal"]
    total_threads = profile["threadsTotal"]
    labels = auth_client.users().labels().get(userId="me", id="INBOX").execute()
    unread_count = labels.get("messagesUnread", 0)
    return f"Email: {email}, Total messages: {total_messages}, Total threads: {total_threads}, Unread Emails: {unread_count}"




#Read your emails

@app.tool()
def read_mail():
    auth_client = get_gmail_service()
    message_list = auth_client.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=10
    ).execute()

    all_messages = []

    for msg in message_list.get("messages", []):
        msg_data = auth_client.users().messages().get(
            userId="me",
            id=msg["id"]
        ).execute()

        payload = msg_data["payload"]
        headers = payload.get("headers", [])

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
        from_email = next((h["value"] for h in headers if h["name"] == "From"), "")
        date_received = next((h["value"] for h in headers if h["name"] == "Date"), "")
        body_text = ""
        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain":
                    data = part.get("body", {}).get("data")
                    if data:
                        body_text = base64.urlsafe_b64decode(data).decode("utf-8")
                        break

        else:
            data = payload.get("body", {}).get("data")
            if data:
                body_text = base64.urlsafe_b64decode(data).decode("utf-8")

        
        if not body_text:
            body_text = msg_data.get("snippet", "")

        all_messages.append({
            "from": from_email,
            "subject": subject,
            "body": body_text,
            "date": date_received
        })

    return all_messages





#Send an email
@app.tool()
def write_and_send_mail(send_email: str, send_subject: str, send_message: str):
    auth_client=get_gmail_service()
    msg = EmailMessage()
    msg["To"] = send_email
    msg["Subject"] = send_subject
    msg.set_content(send_message)

    raw_bytes = msg.as_bytes()
    encoded_message = base64.urlsafe_b64encode(raw_bytes).decode()

    
    auth_client.users().messages().send(
        userId="me",
        body={"raw": encoded_message}
    ).execute()

    return f"Email sent to {send_email} successfully"


#Email Summary
@app.tool()
def summarize_mail():
    messages = read_mail()
    summaries = []

    for msg in messages:
        text = f"{msg['subject']}: {msg['body']}"
        summaries.append(text)
    return summaries

if __name__ == "__main__":
    logger.info("Starting Gmail MCP server via __main__")
    app.run()