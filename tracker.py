import bencode
import aiohttp
import logging
import collections
import urllib.parse

from enum import StrEnum
from config import LOGGING_LEVEL

logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)


class Events(StrEnum):
    STARTED = "started"
    STOPPED = "stopped"
    COMPLETED = "completed"


class Peer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port


class Tracker:
    def __init__(self, torrent, peer_id):
        self._torrent = torrent
        self._peer_id = peer_id
        logger.debug("Tracker initialized")

    async def get_peers(self) -> list[Peer] | None:
        """Returns array of parsed peers."""
        data = await self._request_peers_data()
        if not data:
            logger.warning("Failed to get peers")
            return None
        peers = self._parse_peers(data["peers"])
        for peer in peers:
            logger.debug(f"Received peer: {peer}")
        logger.info(f"Received peers total count: {len(peers)}")
        return [Peer(ip=peer[0], port=peer[1]) for peer in peers]

    async def _request_peers_data(self) -> collections.OrderedDict | None:
        """Makes https request to get data from torrent and returns this data if successful
        and returns None otherwise."""
        url = f"{self._torrent.announce_url}?{self._get_quoted_parameters()}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.read()
                        logger.debug(f"Received data from torrent")
                        return bencode.decode(data)
                    else:
                        logger.error(f"Failed to get peers. Error: {response.status}")
        except Exception as e:
            logger.error(f"Failed to get data from torrent: {e}")

    def _get_parameters(self) -> dict[str, str | int | bytes]:
        """Returns dictionary of unquoted parameters for https request."""
        return {
            "info_hash": self._torrent.info_hash(),
            "peer_id": self._peer_id,
            "port": 6881,
            "uploaded": 0,
            "downloaded": 0,
            "left": self._torrent.size,
            "event": Events.STARTED
        }

    def _get_quoted_parameters(self) -> str:
        """Returns dictionary of quoted parameters for https request."""
        return "&".join(
            f"{key}={urllib.parse.quote_from_bytes(value) if key == 'info_hash' else urllib.parse.quote(str(value))}"
            for key, value in self._get_parameters().items())

    @staticmethod
    def _parse_peers(data: str) -> list[tuple[str, str]]:
        """Parses peers and returns array of them."""
        peers = []
        for i in range(0, len(data), 6):
            ip = '.'.join(f"{block}" for block in data[i:i + 4])
            port = str(data[i + 4] * 256 + data[i + 5])  # умножаем на 256 для сдвига на 8 битов влево
            peers.append((ip, port))
        logger.debug(f"Parsed ips and hosts")
        return peers
