import asyncio
import logging

from torrent import Torrent
from tracker import Tracker
from file_saver import FileSaver
from config import LOGGING_LEVEL
from utils import generate_peer_id
from collections import defaultdict
from peer_connection import PeerConnection

logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)

__author__ = "https://github.com/kla1mn"


async def main():
    file_name = "Torrent files/green_day.torrent"
    logging.debug(f"Starting torrent download: {file_name}")
    try:
        data = Torrent(file_name)
        file_saver = FileSaver(data)
        peer_id = generate_peer_id()
        tracker = Tracker(data, peer_id)
        peers = await tracker.get_peers()
        piece_rarity = defaultdict(int)
        connections = [PeerConnection(peer.ip, peer.port, data, peer_id, piece_rarity) for peer in peers]
        tasks = [peer.download() for peer in connections]
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.debug(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
