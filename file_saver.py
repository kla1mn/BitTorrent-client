import os


class FileSaver:
    def __init__(self, torrent):
        self.files = torrent.files
        self._create_empty_files()

    def _create_empty_files(self) -> None:
        """Creates empty directories anf files if they don't exist."""
        for file in self.files:
            file_path = os.path.join(file.directory, file.name) if file.directory else file.name
            if file.directory:
                os.makedirs(file.directory, exist_ok=True)
            with open(file_path, 'wb') as f:
                f.seek(file.length - 1)
                f.write(b'\0')
