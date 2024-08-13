import asyncio
import torrent
import logging

from tracker import Tracker
from file_saver import FileSaver
from config import LOGGING_LEVEL
from utils import generate_peer_id
from peer_connection import PeerConnection

logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)


async def main():
    file_name = "Torrent files/stray.torrent"
    logging.debug(f"Starting torrent download: {file_name}")
    try:
        data = torrent.Torrent(file_name)
        file_saver = FileSaver(data)
        peer_id = generate_peer_id()
        tracker = Tracker(data, peer_id)
        peers = await tracker.get_peers()
        connections = [PeerConnection(peer.ip, peer.port) for peer in peers]
        tasks = [peer_connection.download() for peer_connection in connections]
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.debug(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
