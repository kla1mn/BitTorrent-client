import torrent
from file_saver import FileSaver


if __name__ == "__main__":
    file_name = "stray.torrent"
    torrent = torrent.Torrent(file_name)
    file_saver = FileSaver(torrent)
