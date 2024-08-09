import bencode
from collections import OrderedDict
from file import File


class Torrent:
    def __init__(self, file):
        data = Torrent.decode_file(file)
        self._data = data
        self._encoding = data['encoding']
        self._announce = data['announce']
        self._announce_list = data['announce-list']
        self._info = info = data['info']

        if 'length' in info:
            self._length = info['length']  # если один файл
        if 'files' in info:
            self._files = info['files']  # если несколько файлов

        # название файла или директории, куда надо сохранить контент
        self._name = info['name']

        # строка с длиной кратной 20, каждый кусок длиной 20 у разбитой строки, это SHA1 hash соответсвующего куска
        self._pieces = info['pieces']

        # количество байтов в каждом куске файла
        self._pieces_length = info['piece length']
        self.files = Torrent.create_files(info)

    @staticmethod
    def decode_file(torrent_file: str) -> OrderedDict:
        """Returns ordered dictionary with torrent data."""
        with open(torrent_file, "rb") as file:
            data = file.read()
        return bencode.decode(data)

    @staticmethod
    def create_files(info):
        # TODO docs
        if "length" in info:
            return [File(info["name"], info["length"])]

        files = []
        for data in info["files"]:
            parts = [info["name"]] + data["path"]
            path = "/".join(parts)
            files.append(File(path, data["length"]))
        return files
