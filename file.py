class File:
    def __init__(self, name, length):
        self.path = name
        self.length = length

    def __str__(self):
        return f'path: {self.path}, length: {self.length}'
