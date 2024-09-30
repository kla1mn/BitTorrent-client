import os
import logging
import aiofiles

from config import LOGGING_LEVEL

logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)


class FileSaver:
    def __init__(self, torrent):
        self.files = torrent.files
        self.piece_length = torrent.bytes_count_per_piece
        self.total_length = torrent.size
        self.torrent = torrent
        logger.debug("File saver initialized")

    async def create_empty_files(self) -> None:
        """Creates empty directories and files if they don't exist."""
        for file in self.files:
            file_path = os.path.join(file.directory, file.name)
            try:
                os.makedirs(file.directory, exist_ok=True)
                async with aiofiles.open(file_path, 'wb') as f:
                    await f.seek(file.length - 1)
                    await f.write(b'\0')
                logger.debug(f"Created file: {file_path}")
            except Exception as e:
                logger.error(f"Error creating file: {file_path}, {e}")
        logger.info("All empty files created in their directories")

    async def save_piece(self, piece_index, piece_data):
        """Save a piece to the appropriate file(s)."""
        piece_start = piece_index * self.piece_length
        piece_end = min(piece_start + len(piece_data), self.total_length)

        current_pos = piece_start
        for file in self.files:
            file_path = os.path.join(file.directory, file.name)
            file_start = sum(f.length for f in self.files[:self.files.index(file)])
            file_end = file_start + file.length

            if current_pos >= file_end:
                continue
            if current_pos < file_start:
                current_pos = file_start

            async with aiofiles.open(file_path, 'r+b') as f:
                await f.seek(current_pos - file_start)
                bytes_to_write = min(piece_end - current_pos, file_end - current_pos)
                await f.write(piece_data[current_pos - piece_start:current_pos - piece_start + bytes_to_write])

            current_pos += bytes_to_write
            if current_pos >= piece_end:
                break

        logger.debug(f"Saved piece {piece_index} to file(s)")
