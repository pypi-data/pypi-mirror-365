import smtplib

class EmailSender:
    def __init__(self, service, login: str, password: str):
        self.service = service
        self.login = login
        self.password = password

    def send(self, to_email: str, msg) -> str:
        try:
            with smtplib.SMTP(self.service.server, self.service.port) as server:
                server.starttls()
                server.login(self.login, self.password)
                server.sendmail(self.login, to_email, msg.as_string())
            return "Email sent successfully"
        except Exception as e:
            return f"Error sending email: {e}"
