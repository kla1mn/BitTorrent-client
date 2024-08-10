import hashlib
import bencode

from collections import OrderedDict
from file import File


class Torrent:
    def __init__(self, file):
        self._data = Torrent.decode_file(file)
        self._announce_url = self._data['announce']
        # self._announce_list = self._data['announce-list']
        self._info = self._data['info']
        self._name = self._info['name']
        self._pieces = self._info['pieces']
        self._bytes_count_per_piece = self._info['piece length']
        self._files = Torrent.create_files(self._info)
        self.size = sum(file.length for file in self.files)

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
        """Returns ordered dictionary with torrent data."""
        with open(torrent_file, "rb") as file:
            data = file.read()
        return bencode.decode(data)

    @staticmethod
    def create_files(info: dict) -> list[File]:
        """Returns list with torrent file if content contains only one file and array of files otherwise."""
        return [File(info["name"], info["length"])] \
            if "length" in info \
            else [File("/".join([info["name"]] + file["path"]), file["length"]) for file in info["files"]]
