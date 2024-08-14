import asyncio
import logging

from config import LOGGING_LEVEL

logger = logging.getLogger(__name__)
logging.basicConfig(level=LOGGING_LEVEL)


class PeerConnection:
    def __init__(self, ip, port, torrent, peer_id):
        self._ip, self._port = ip, port
        self._torrent = torrent
        self._peer_id = peer_id
        self._reader, self._writer = None, None
        self.chocked = True

    async def download(self):
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self._ip, self._port), timeout=5)
        except Exception as e:
            logger.error(f"Failed to connect to {self._ip}:{self._port}, reason: {e}")
            return

        logger.debug("Send handshake")
        handshake = self._generate_handshake()
        await self._write(handshake)

        response = await self._read(len(handshake))
        if not response:
            logger.error("Failed to receive handshake")
            return
        logger.info(f"Got handshake, peer id: {response[48:]}")

        self._writer.close()
        await self._writer.wait_closed()
        logger.debug(f"Connection closed")

    async def _read(self, n):
        try:
            return await self._reader.readexactly(n)
        except Exception as e:
            logger.error(f"Failed to read from {self._ip}:{self._port}, reason: {e}")
            return b""

    async def _write(self, data):
        self._writer.write(data)
        logger.debug(f"Writing data to {self._ip}:{self._port}")
        await self._writer.drain()

    def _generate_handshake(self) -> bytes:
        return b"".join([chr(19).encode(),
                         b"BitTorrent protocol",
                         b"\0" * 8,
                         self._torrent.info_hash(),
                         self._peer_id.encode()])
