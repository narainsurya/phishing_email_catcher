import os
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# -----------------------------------------
# CONFIGURATION
# -----------------------------------------
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CRED_FILE = 'credentials.json'   # Your OAuth client file
TOKEN_FILE = 'token.json'        # Created after first successful login
ATTACH_DIR = 'attachments'       # Folder to save attachments

# -----------------------------------------
# STEP 1: Authenticate and Build Service
# -----------------------------------------
def get_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CRED_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

# -----------------------------------------
# STEP 2: Extract Plain Text Body
# -----------------------------------------
def extract_plain_text_from_parts(parts):
    """Recursively extract text/plain from message parts."""
    if not parts:
        return None
    for part in parts:
        if part.get('parts'):
            text = extract_plain_text_from_parts(part['parts'])
            if text:
                return text
        mime = part.get('mimeType', '')
        body = part.get('body', {})
        data = body.get('data')
        if mime == 'text/plain' and data:
            return base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8', errors='replace')
    return None

# -----------------------------------------
# STEP 3: Download Attachments
# -----------------------------------------
def save_attachments(service, msg_id):
    """Downloads all attachments from a Gmail message."""
    if not os.path.exists(ATTACH_DIR):
        os.makedirs(ATTACH_DIR, exist_ok=True)

    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    payload = msg.get('payload', {})
    parts = payload.get('parts', [])
    saved_files = []

    for part in parts:
        filename = part.get('filename')
        body = part.get('body', {})
        if filename and 'attachmentId' in body:
            att_id = body['attachmentId']
            att = service.users().messages().attachments().get(
                userId='me', messageId=msg_id, id=att_id
            ).execute()
            data = base64.urlsafe_b64decode(att['data'].encode('UTF-8'))
            path = os.path.join(ATTACH_DIR, filename)
            with open(path, 'wb') as f:
                f.write(data)
            saved_files.append(path)

    return saved_files

# -----------------------------------------
# STEP 4: Fetch Email Details
# -----------------------------------------
def get_email_details(service, msg_id):
    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    payload = msg.get('payload', {})

    # Extract headers
    headers = {h['name']: h['value'] for h in payload.get('headers', [])}
    sender = headers.get('From', '(No Sender)')
    subject = headers.get('Subject', '(No Subject)')

    # Extract body
    body = extract_plain_text_from_parts(payload.get('parts', []))
    if not body:
        data = payload.get('body', {}).get('data')
        if data:
            body = base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8', errors='replace')
        else:
            body = msg.get('snippet', '')

    # Extract attachments
    attachments = save_attachments(service, msg_id)

    return {
        "from": sender,
        "subject": subject,
        "body": body.strip(),
        "attachments": attachments
    }

# -----------------------------------------
# STEP 5: Main Function
# -----------------------------------------
def main():
    service = get_service()

    print("Fetching latest 10 emails...\n")
    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No messages found.")
        return

    for i, msg in enumerate(messages, 1):
        email_data = get_email_details(service, msg['id'])
        print(f"\n================ Email {i} ================\n")
        print(f"From: {email_data['from']}")
        print(f"Subject: {email_data['subject']}\n")
        print(f"Body:\n{email_data['body'][:300]}")  # print only first 300 chars
        if email_data['attachments']:
            print(f"\nAttachments saved: {', '.join(email_data['attachments'])}")
        else:
            print("\nAttachments: None")
        print("\n===========================================")

if __name__ == '__main__':
    main()
