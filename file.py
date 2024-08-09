class File:
    def __init__(self, name, length):
        self.name = name
        self.length = length

    def __str__(self):
        return f'name: {self.name}, length: {self.length}'
