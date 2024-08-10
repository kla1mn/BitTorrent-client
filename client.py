import asyncio
import torrent
from file_saver import FileSaver
from peer import Peer
from tracker import Tracker


async def main():
    file_name = "Torrent files/stray.torrent"
    data = torrent.Torrent(file_name)
    file_saver = FileSaver(data)
    peer = Peer()
    tracker = Tracker(data, peer.peer_id)

    await tracker.get_peers()


if __name__ == "__main__":
    asyncio.run(main())
