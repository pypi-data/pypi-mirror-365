import os
import mimetypes
from email.mime.base import MIMEBase
from email import encoders

class AttachmentHandler:
    def __init__(self, validator):
        self.validator = validator

    def add_attachments(self, msg, file_paths):
        self.validator.validate(file_paths)
        for path in file_paths:
            mime_type, _ = mimetypes.guess_type(path)
            if not mime_type:
                raise ValueError(f"Unsupported MIME type for file {path}")

            main, sub = mime_type.split("/")
            with open(path, "rb") as f:
                part = MIMEBase(main, sub)
                part.set_payload(f.read())
                encoders.encode_base64(part)

            filename = os.path.basename(path)
            part.add_header("Content-Disposition", f"attachment; filename={filename}")
            msg.attach(part)
