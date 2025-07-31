from .email_sender import EmailSender
from .email_builder import EmailBuilder
from .file_validator import FileValidator
from .attachment_handler import AttachmentHandler

class EmailClient:
    def __init__(self, service, login, password):
        self.service = service
        self.sender = EmailSender(service, login, password)
        self.builder = EmailBuilder(login)
        self.validator = FileValidator(service)
        self.attachment_handler = AttachmentHandler(self.validator)

    def send_email(self, to, subject, body, files=None, cc=None, bcc=None, body_type="plain"):
        msg = self.builder.build(to, subject, body, body_type, cc, bcc)
        if files:
            self.attachment_handler.add_attachments(msg, files)
        return self.sender.send(to, msg)
