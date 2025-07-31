import os

class FileValidator:
    def __init__(self, service):
        self.service = service

    def validate(self, files):
        total_size = 0
        for file in files:
            if not os.path.isfile(file):
                raise FileNotFoundError(f"File {file} does not exist.")
            total_size += os.path.getsize(file)

        if total_size > self.service.max_size_bytes:
            raise ValueError("Total attachment size exceeds the limit.")
