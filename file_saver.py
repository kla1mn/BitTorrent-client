import os


class FileSaver:
    def __init__(self, torrent):
        self.files = torrent.files
        self._create_empty_files()

    def _create_empty_files(self):
        for file in self.files:
            file_path = file.name
            if hasattr(file, "directory"):
                file_path = os.path.join(file.directory, file.name)
                os.makedirs(file.directory, exist_ok=True)
            with open(file_path, 'w') as f:
                f.seek(file.length - 1)
                f.write('0')
