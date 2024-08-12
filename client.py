import asyncio
import torrent
import logging

from peer_id import PeerId
from tracker import Tracker
from file_saver import FileSaver
from config import LOGGING_LEVEL

logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)


async def main():
    file_name = "Torrent files/amanita.torrent"
    logging.debug(f"Starting torrent download: {file_name}")
    try:
        data = torrent.Torrent(file_name)
        file_saver = FileSaver(data)
        peer = PeerId()
        tracker = Tracker(data, peer.peer_id)
        peers = await tracker.get_peers()
    except Exception as e:
        logger.debug(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
