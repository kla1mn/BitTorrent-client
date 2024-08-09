class File:
    def __init__(self, path, length):
        self.path = path
        self.length = length

    def __str__(self):
        return f'path: {self.path}, length: {self.length}'
