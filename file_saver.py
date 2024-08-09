class FileSaver:
    def __init__(self, torrent):
        self.files = torrent.files
        self._create_empty_file()

    def _create_empty_file(self):
        for file in self.files:
            with open(file, 'wb') as f:
                f.seek(file.length - 1)
                f.write(b'\0')
