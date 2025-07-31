import sys
import os
from dotenv import load_dotenv

load_dotenv()  # load content in file .env

email_sender = os.getenv('EMAIL_SENDER')  # get sender email

email_dest = os.getenv('EMAIL_DEST') # get email dest

email_password = os.getenv('EMAIL_PASSWORD')  # get application password

email_cc = os.getenv('EMAIL_CC') # copy recipient

email_bcc = os.getenv('EMAIL_BCC') # hidden copy recipient


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

list_files = [
    os.path.join(BASE_DIR, "random.hpp"),
    os.path.join(BASE_DIR, "test.pdf")
]


from lycosa.sender import EmailClient, Gmail

# Choose the email service : Gmail, Orange
service = Gmail()

# Login credentials
login = email_sender
password = email_password  # application password

# Create a customer
client = EmailClient(service, login, password)


html_message = """
<html>
    <body>
        <h1 style="color:blue;">This is an HTML test!</h1>
        <p>Sending an email in <b>HTML</b> with an attachment.</p>
    </body>
</html>
"""

txt_message = "This is a test of sending email through my library."

# Send a simple email
result = client.send_email(
    to=email_dest,
    subject="Hello",
    body=html_message,
    files=[list_files[0], list_files[1]],
    cc=["collaborateur@example.com"],
    bcc=["boss@example.com"], 
    body_type="html"
)

print(result) 