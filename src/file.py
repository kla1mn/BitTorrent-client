import os
import logging

from config import LOGGING_LEVEL

logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)


class File:
    def __init__(self, directory, length):
        self.directory = os.path.dirname(directory)
        self.name = os.path.basename(directory)
        self.length = length
        logger.debug(f"File {self.name} initialized")

    def __str__(self):
        return f'name: {self.name}, directory: {self.directory}, length: {self.length}'
