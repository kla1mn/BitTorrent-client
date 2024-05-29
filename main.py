from collections import OrderedDict

import bencode


def decode_torrent_file(torrent_file: str) -> OrderedDict:
    """Returns ordered dictionary with torrent data."""
    with open(torrent_file, "rb") as f:
        data = f.read()

    return bencode.decode(data)


if __name__ == "__main__":
    file_name = "[M1] Stray [P] [RUS + ENG + 14] (2022) (1.5) [App Store] [rutracker-6452328].torrent"
    decode_torrent_file(file_name)
    