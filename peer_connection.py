import asyncio
import logging
import bitstring

from enum import IntEnum
from config import LOGGING_LEVEL

logger = logging.getLogger(__name__)
logging.basicConfig(level=LOGGING_LEVEL)


class MessageType(IntEnum):
    CHOKE = 0,
    UNCHOKE = 1
    INTERESTED = 2
    NOT_INTERESTED = 3
    HAVE = 4
    BITFIELD = 5
    REQUEST = 6
    PIECE = 7
    CANCEL = 8


class PeerConnection:
    def __init__(self, ip, port, torrent, peer_id):
        self._ip, self._port = ip, port
        self._torrent = torrent
        self._peer_id = peer_id
        self._reader, self._writer = None, None
        self._chocked = True
        self._have_pieces = None

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

        while True:
            len_bytes = await self._read(4)
            if not len_bytes:
                logger.debug("No more bytes. Disconnecting")
                break

            len_value = int.from_bytes(len_bytes, byteorder='big')
            logger.debug(f"Received {len_value} bytes")
            if len_value == 0:
                logger.debug("Keep alive")
                continue

            message = await self._read(len_value)
            if not message:
                logger.debug("Can't read message. Disconnecting")
                break

            message_id = int(message[0])

            if message_id == MessageType.CHOKE:
                logger.debug("Message: Choke")
                self._chocked = True
            elif message_id == MessageType.UNCHOKE:
                logger.debug("Message: Unchoke")
                self._chocked = False
            elif message_id == MessageType.INTERESTED:
                logger.debug("Message: Interested")
            elif message_id == MessageType.NOT_INTERESTED:
                logger.debug("Message: Not Interested")
            elif message_id == MessageType.HAVE:
                logger.debug("Message: Have")
            elif message_id == MessageType.BITFIELD:
                self._have_pieces = bitstring.BitArray(bytes=message[1:], length=self._torrent.pieces_count)
                logger.debug(f"Message: Bit field hex: {self._have_pieces}")
                bitfield_binary = ''.join(format(byte, '08b') for byte in message[1:])
                logger.debug(f"Message: Bit field bin: {bitfield_binary}")
                interested_message = b"\0\0\0\1\2"
                logger.debug(f"Sending message: Interested")
                await self._write(interested_message)

            elif message_id == MessageType.REQUEST:
                logger.debug("Message: Request")
            elif message_id == MessageType.PIECE:
                logger.debug("Message: Piece")
            elif message_id == MessageType.CANCEL:
                logger.debug("Message: Cancel")
            else:
                logger.debug(f"Message: Unknown message type: {message_id}")

        self._writer.close()
        await self._writer.wait_closed()
        logger.debug("Connection closed")

    async def _read(self, n):
        try:
            data = await self._reader.readexactly(n)
            return data
        except asyncio.IncompleteReadError as e:
            logger.error(f"Incomplete read error: expected {n} bytes, but got {len(e.partial)} bytes")
            return e.partial
        except Exception as e:
            logger.error(f"Failed to read {n} bytes, reason: {str(e)}")
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
