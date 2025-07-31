# lycosa

lycosa is a python library that allows you to easily manage emails


## Installation 

bash
```
pip install lycosa
```

## Use

python
```
from lycosa.sender import EmailClient, Gmail

# Choose the email service : Gmail, Orange
service = Gmail()

# Login credentials
login = "test@gmail.com"            # sender email
password = "erfd dfess rftes fres"  # application password

# Create a customer
client = EmailClient(service, login, password)

list_files = ["text.txt", "image.png", "doc.pdf"]

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
    files=[list_files[0], list_files[1], list_files[2]],
    cc=["collaborateur@example.com"],
    bcc=["boss@example.com"], 
    body_type="html"
)

print(result) 
```


## 