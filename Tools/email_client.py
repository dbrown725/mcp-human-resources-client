import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import imaplib
import email
import os
import datetime

# Replace these with your Gmail credentials
EMAIL_ADDRESS = os.getenv('GMAIL_EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('GMAIL_EMAIL_APP_PASSWORD') # gmail account's app specific password, not actual gmail user login password.

class GmailClient:
    def __init__(self, email_address, email_password):
        self.email_address = email_address
        self.email_password = email_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993

    def format_subject_string(self, input_string):
        # Replace underscores with spaces
        formatted_string = input_string.replace('_', ' ')
        # Capitalize the first character of each word
        formatted_string = formatted_string.title()
        return formatted_string

    def send_email(self, to_email, subject, body, attachment_paths=None):
        # Create MIMEMultipart object
        msg = MIMEMultipart()
        msg['Subject'] = self.format_subject_string(subject)
        msg['From'] = self.email_address
        msg['To'] = to_email

        # Attach the body with the msg instance
        msg.attach(MIMEText(body, 'plain'))

        # Attach files if provided
        if attachment_paths:
            for attachment_path in attachment_paths:
                if os.path.isfile(attachment_path):
                    with open(attachment_path, "rb") as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(attachment_path)}")
                        msg.attach(part)
                else:
                    print(f"Warning: File not found: {attachment_path}")

        # Connect to SMTP server and send the email
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.sendmail(self.email_address, to_email, msg.as_string())
            # print(f"Email sent to {to_email}")

    def save_draft(self, to_email, subject, body, attachment_paths=None):
        # Create MIMEMultipart object
        msg = MIMEMultipart()
        msg['Subject'] = self.format_subject_string(subject)
        msg['From'] = self.email_address
        msg['To'] = to_email

        # Attach the body with the msg instance
        msg.attach(MIMEText(body, 'plain'))

        # Attach files if provided
        if attachment_paths:
            for attachment_path in attachment_paths:
                if os.path.isfile(attachment_path):
                    with open(attachment_path, "rb") as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(attachment_path)}")
                        msg.attach(part)
                else:
                    print(f"Warning: File not found: {attachment_path}")

        # Get the current date and time
        current_datetime = datetime.datetime.now()

        # Convert the datetime to an IMAP internal date format
        date_time_str = imaplib.Time2Internaldate(current_datetime.timestamp())

        # Connect to IMAP server and save the email as a draft
        with imaplib.IMAP4_SSL(self.imap_server, self.imap_port) as imap:
            imap.login(self.email_address, self.email_password)
            imap.select('[Gmail]/Drafts')
            imap.append('[Gmail]/Drafts', '', date_time_str, (msg.as_string()).encode('utf-8'))
            # print("Draft saved to Gmail")

def handle_save_draft_request(to_email, subject, body, attachment_paths):
    gmail_client = GmailClient(EMAIL_ADDRESS, EMAIL_PASSWORD)
    gmail_client.save_draft(to_email, subject, body, attachment_paths)            

if __name__ == "__main__":
    # Example usage
    gmail_client = GmailClient(EMAIL_ADDRESS, EMAIL_PASSWORD)

    # Send an email with multiple attachments
    # gmail_client.send_email(
    #     to_email="",
    #     subject="Test Subject",
    #     body="This is a test email body.",
    #     attachment_paths=["/home/vboxuser/Documents/projects/openmanuswork/work_area/laureate_education/laureate_education.html", 
    #                       "/home/vboxuser/Documents/projects/openmanuswork/work_area/laureate_education/laureate_education.pdf",
    #                       "/home/vboxuser/Documents/projects/openmanuswork/work_area/laureate_education/laureate_education.docx"]
    # )

    # Save a draft with multiple attachments
    gmail_client.save_draft(
        to_email="",
        subject="Draft Subject",
        body="This is a draft email body.",
        attachment_paths=[]
    )