import logging
import os
from typing import Optional
import filetype
from src.util.os import get_file_location

# TODO: move to local settings and app settings
FILE_TYPES = ["tif", "pdf", "jpeg", "jpg", "png", "gif", "bmp", "csv"]


class FileRepository:
    def __init__(self, filename: str, contents: bytes):
        self.filename = filename
        self.file_path = get_file_location()
        self.contents = contents
        self.file_fullpath = os.path.join(self.file_path, self.filename)

    def get_mime(self) -> Optional[str]:
        kind = filetype.guess(self.file_fullpath)
        if kind is None:
            logging.error("Can not parse file type")
            return None
        return str(kind.mime)

    def write(self) -> bool:
        try:
            with open(self.file_fullpath, "wb") as file:
                file.write(self.contents)
        except IOError as ex:
            logging.error("Creating temp file failed, error: %s", ex)
            return False
        return True

    def is_valid(self) -> bool:
        file_types = FILE_TYPES
        is_valid = any(
            self.filename.lower().endswith(file_type) for file_type in file_types
        )
        return is_valid
