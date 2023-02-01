import os
import tempfile


def get_file_location() -> str:
    if os.getenv("FILE_PATH"):
        return str(os.getenv("FILE_PATH"))
    else:
        return tempfile.gettempdir()
