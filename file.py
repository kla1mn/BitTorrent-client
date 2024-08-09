class File:
    def __init__(self, name, length, directory=None):
        if directory is not None:
            self.directory = directory
        self.name = name
        self.length = length

    def __str__(self):
        return f'directory: {self.directory}, name: {self.name}, length: {self.length}' \
            if hasattr(self, 'directory') \
            else f'directory: no directory, name: {self.name}, length: {self.length}'
