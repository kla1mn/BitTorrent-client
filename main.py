import torrent
from file_saver import FileSaver


if __name__ == "__main__":
    file_name = "stray.torrent"
    torrent = torrent.Torrent(file_name)
    fs = FileSaver(torrent)
    for file in fs.files:
        print(file)
