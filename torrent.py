import hashlib
import logging
import bencode

from file import File
from collections import OrderedDict
from config import LOGGING_LEVEL

logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)


class Torrent:
    def __init__(self, file):
        self._data = Torrent.decode_file(file)
        logger.debug("Torrent data decoded")
        self._announce_url = self._data['announce']
        # self._announce_list = self._data['announce-list']
        self._info = self._data['info']
        self._name = self._info['name']
        self._pieces = self._info['pieces']
        self._bytes_count_per_piece = self._info['piece length']
        logger.debug("Created fields with torrent info")
        self._files = Torrent.create_files(self._info)
        logger.debug("Received list with directories of torrent files")
        self.size = sum(file.length for file in self.files)

    @property
    def name(self):
        return self._name

    @property
    def announce_url(self):
        return self._announce_url

    @property
    def files(self):
        return self._files

    def info_hash(self) -> bytes:
        """Returns hash of info's dictionary of torrent data in bytes."""
        return hashlib.sha1(bencode.encode(self._info)).digest()

    @staticmethod
    def decode_file(torrent_file: str) -> OrderedDict:
        """Returns decoded ordered dictionary with data from bencoded torrent file."""
        with open(torrent_file, "rb") as file:
            data = file.read()
        logger.debug(f"Read bencoded data from {torrent_file}")
        return bencode.decode(data)

    @staticmethod
    def create_files(info: dict) -> list[File]:
        """Returns list with torrent file if content contains only one file and array of files otherwise."""
        return [File(info["name"], info["length"])] \
            if "length" in info \
            else [File("/".join([info["name"]] + file["path"]), file["length"]) for file in info["files"]]
