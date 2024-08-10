import asyncio
import torrent

from peer_id import PeerId
from tracker import Tracker
from file_saver import FileSaver


async def main():
    file_name = "Torrent files/amanita.torrent"
    data = torrent.Torrent(file_name)
    # file_saver = FileSaver(data)
    peer = PeerId()
    tracker = Tracker(data, peer.peer_id)
    await tracker.get_peers()


if __name__ == "__main__":
    asyncio.run(main())
