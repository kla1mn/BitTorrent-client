import hashlib
import bencode

from collections import OrderedDict
from file import File


class Torrent:
    def __init__(self, file):
        self._data = Torrent.decode_file(file)
        self._announce = self._data['announce']
        self._announce_list = self._data['announce-list']
        self._info = self._data['info']
        self._name = self._info['name']
        self._pieces = self._info['pieces']
        self._bytes_count_per_piece = self._info['piece length']
        self.files = Torrent.create_files(self._info)

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

    def info_hash(self) -> bytes:
        """Returns nash of info's dictionary of torrent data in bytes."""
        return hashlib.sha1(bencode.encode(self._info)).digest()
