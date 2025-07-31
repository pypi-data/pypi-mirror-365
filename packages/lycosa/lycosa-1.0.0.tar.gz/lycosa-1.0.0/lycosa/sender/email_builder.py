from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailBuilder:
    def __init__(self, sender_email: str):
        self.sender_email = sender_email

    def build(self, to, subject, body, body_type="plain", cc=None, bcc=None):
        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = to
        msg["Subject"] = subject

        if cc:
            msg["Cc"] = ', '.join(cc)
        if bcc:
            msg["Bcc"] = ', '.join(bcc)

        msg.attach(MIMEText(body, body_type))
        return msg
