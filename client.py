import torrent
from file_saver import FileSaver


def main():
    file_name = "amanita.torrent"
    data = torrent.Torrent(file_name)
    file_saver = FileSaver(data)


if __name__ == "__main__":
    main()
