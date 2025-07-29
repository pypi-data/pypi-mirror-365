import base64
from pathlib import Path


def base64_encode(file: Path):
    file_bytes = file.read_bytes()
    return base64.b64encode(file_bytes)
