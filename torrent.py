import bencode
from collections import OrderedDict
from file import File


class Torrent:
    def __init__(self, file):
        data = Torrent.decode_file(file)
        self._data = data
        self._announce = data['announce']
        self._announce_list = data['announce-list']
        self._info = info = data['info']
        self._name = info['name']

        # строка с длиной кратной 20, каждый кусок длиной 20 у разбитой строки, это SHA1 hash соответсвующего куска
        self._pieces = info['pieces']
        self._bytes_count_per_piece = info['piece length']
        self.files = Torrent.create_files(info)

    @staticmethod
    def decode_file(torrent_file: str) -> OrderedDict:
        """Returns ordered dictionary with torrent data."""
        with open(torrent_file, "rb") as file:
            data = file.read()
        return bencode.decode(data)

    @staticmethod
    def create_files(info: dict) -> list[File]:
        """Returns list with torrent file if content contains only one file and array of files otherwise."""
        if "length" in info:
            return [File(info["name"], info["length"])]
        files = []
        for file in info["files"]:
            files.append(File('/'.join(file["path"]), file["length"]))
        return files
