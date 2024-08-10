import bencode
import aiohttp
import collections
import urllib.parse

from enum import StrEnum


class Events(StrEnum):
    STARTED = "started"
    STOPPED = "stopped"
    COMPLETED = "completed"


class Tracker:
    def __init__(self, torrent, peer_id):
        self._torrent = torrent
        self._peer_id = peer_id

    async def get_peers(self) -> list[tuple[str, str]]:
        """Returns array of parsed peers."""
        data = await self._request_peers_data()
        peers = self._parse_peers(data["peers"])
        return peers

    async def _request_peers_data(self) -> collections.OrderedDict | None:
        """Makes https request to get data from torrent and returns this data if successful
        and returns None otherwise."""
        url = f"{self._torrent.announce_url}?{self._get_quoted_parameters()}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.read()
                        return bencode.decode(data)
                    else:
                        print(f"Response error: {response.status}")
        except Exception as e:
            print(f"Exception: {e}")

    def _get_parameters(self) -> dict[str, str | int | bytes]:
        """Returns dictionary of unquoted parameters for https request."""
        return {
            "info_hash": self._torrent.info_hash(),
            "peer_id": self._peer_id,
            "port": 6881,
            "uploaded": 0,
            "downloaded": 0,
            "left": self._torrent.size,
            "event": Events.STARTED.value
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
        return peers
