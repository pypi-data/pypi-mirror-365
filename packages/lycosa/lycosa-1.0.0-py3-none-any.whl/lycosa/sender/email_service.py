class EmailService:
    def __init__(self, server: str, port: int, max_size_bytes: int):
        self.server = server
        self.port = port
        self.max_size_bytes = max_size_bytes


class Gmail(EmailService):
    def __init__(self):
        super().__init__("smtp.gmail.com", 587, 25 * 1024 * 1024)


class Orange(EmailService):
    def __init__(self):
        super().__init__("smtp.orange.fr", 465, 25 * 1024 * 1024)
