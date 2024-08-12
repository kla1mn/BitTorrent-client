import os
import logging

from config import LOGGING_LEVEL

logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)


class FileSaver:
    def __init__(self, torrent):
        self.files = torrent.files
        logger.debug("File saver initialized")
        self._create_empty_files()
        logger.info("All empty files created in their directories")

    def _create_empty_files(self) -> None:
        """Creates empty directories and files if they don't exist."""
        for file in self.files:
            file_path = os.path.join(file.directory, file.name) if file.directory else file.name
            try:
                if file.directory:
                    os.makedirs(file.directory, exist_ok=True)
                with open(file_path, 'wb') as f:
                    f.seek(file.length - 1)
                    f.write(b'\0')
                logger.debug(f"Created file: {file_path}")
            except Exception as e:
                logger.error(f"Error creating file: {file_path}, {e}")
