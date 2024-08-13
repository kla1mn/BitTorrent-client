import asyncio
import logging

from config import LOGGING_LEVEL

logger = logging.getLogger(__name__)
logging.basicConfig(level=LOGGING_LEVEL)


class PeerConnection:
    def __init__(self, ip, port):
        self._ip, self._port = ip, port
        self._reader, self._writer = None, None
        self.chocked, self.interested = True, True

    async def download(self):
        try:
            self._reader, self._writer = await asyncio.wait_for(asyncio.open_connection(self._ip, self._port),
                                                                timeout=5)
        except Exception as e:
            logger.error(f"Failed to connect to {self._ip}:{self._port}, reason: {e}")
            return

        self._writer.close()
        await self._writer.wait_closed()
        logger.info(f"Connection closed")
