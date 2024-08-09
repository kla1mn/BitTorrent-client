import os


class File:
    def __init__(self, directory, length):
        self.directory = os.path.dirname(directory)  # TODO проверить на большой вложенности: if directory else ""
        self.name = os.path.basename(directory)  # TODO проверить на большой вложенности: if directory else directory
        self.length = length

    def __str__(self):
        return f'name: {self.name}, directory: {self.directory}, length: {self.length}'
