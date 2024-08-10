import bencode
import aiohttp
import urllib.parse

from enum import StrEnum


class Events(StrEnum):
    started = "started"
    stopped = "stopped"
    completed = "completed"


class Tracker:
    def __init__(self, torrent, peer_id):
        self._torrent = torrent
        self._peer_id = peer_id

    async def get_peers(self):
        data = await self._request_peers_data()
        peers = self._parse_peers(data["peers"])
        for peer in peers:
            print(f"{peer[0]}:{peer[1]}")
        print(f"{len(peers)} peers found")
        return peers

    async def _request_peers_data(self):
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

    def _get_parameters(self):
        return {
            "info_hash": self._torrent.info_hash(),
            "peer_id": self._peer_id,
            "port": 6881,
            "uploaded": 0,
            "downloaded": 0,
            "left": self._torrent.size,
            "event": Events.started.value
        }

    def _get_quoted_parameters(self):
        return "&".join(
            f"{key}={urllib.parse.quote_from_bytes(value) if key == 'info_hash' else urllib.parse.quote(str(value))}"
            for key, value in self._get_parameters().items())

    @staticmethod
    def _parse_peers(data):
        peers = []
        for i in range(0, len(data), 6):
            ip = '.'.join(f"{block}" for block in data[i:i + 4])
            port = data[i + 4] * 256 + data[i + 5]
            peers.append((ip, port))
        return peers
