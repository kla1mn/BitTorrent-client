import asyncio
import logging
import bitstring
import hashlib

from enum import IntEnum

from config import LOGGING_LEVEL

logger = logging.getLogger(__name__)
logging.basicConfig(level=LOGGING_LEVEL)

BLOCK_SIZE = 2 ** 14


class MessageType(IntEnum):
    CHOKE = 0
    UNCHOKE = 1
    INTERESTED = 2
    NOT_INTERESTED = 3
    HAVE = 4
    BITFIELD = 5
    REQUEST = 6
    PIECE = 7
    CANCEL = 8


class PeerConnection:
    def __init__(self, ip, port, torrent, peer_id, file_saver):
        self._ip, self._port = ip, port
        self._torrent = torrent
        self._peer_id = peer_id
        self._reader, self._writer = None, None
        self._choked = True
        self._available_pieces = None
        self._requested_pieces = set()
        self._downloaded_pieces = set()
        self._in_progress_pieces = {}
        self._file_saver = file_saver

    async def process(self):
        await self._file_saver.create_empty_files()

        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self._ip, self._port), timeout=5)
        except Exception as e:
            logger.error(f"Failed to connect to {self._ip}:{self._port}, reason: {e}")
            return

        logger.debug("Send handshake")
        handshake = self._generate_handshake()
        await self._send(handshake)

        response = await self._receive(len(handshake))
        if not response:
            logger.error("Failed to receive handshake")
            return
        logger.info(f"Got handshake, peer id: {response[48:]}")

        while True:
            len_bytes_to_read = await self._receive(4)
            if not len_bytes_to_read:
                logger.debug("No more bytes. Disconnecting")
                break

            len_value_to_read = int.from_bytes(len_bytes_to_read, byteorder='big')
            logger.debug(f"Received {len_value_to_read} bytes of data")
            if len_value_to_read == 0:
                logger.debug("Keep alive")
                continue

            message = await self._receive(len_value_to_read)
            if not message:
                logger.debug("Can't read message. Disconnecting")
                break

            message_id = int(message[0])

            if message_id == MessageType.CHOKE:
                logger.debug("Message: Choke")
                self._choked = True

            elif message_id == MessageType.UNCHOKE:
                logger.debug("Message: Unchoke")
                self._choked = False
                await self._request_pieces()

            elif message_id == MessageType.INTERESTED:
                logger.debug("Message: Interested")

            elif message_id == MessageType.NOT_INTERESTED:
                logger.debug("Message: Not Interested")

            elif message_id == MessageType.HAVE:
                piece_index = int.from_bytes(message[1:5], byteorder='big')
                logger.debug(f"Message: Have piece {piece_index}")
                self._available_pieces[piece_index] = True
                await self._request_pieces()

            elif message_id == MessageType.BITFIELD:
                self._available_pieces = bitstring.BitArray(bytes=message[1:], length=self._torrent.pieces_count)
                logger.debug(f"Message: Bit field: {self._available_pieces}")
                await self._send_interested_message()

            elif message_id == MessageType.REQUEST:
                logger.debug("Message: Request")

            elif message_id == MessageType.PIECE:
                await self._handle_piece(message[1:])

            elif message_id == MessageType.CANCEL:
                logger.debug("Message: Cancel")

            else:
                logger.debug(f"Message: Unknown message type: {message_id}")

        self._writer.close()
        await self._writer.wait_closed()
        logger.debug("Connection closed")

    async def _request_pieces(self):
        if self._choked:
            return

        for i in range(self._torrent.pieces_count):
            if self._available_pieces[i] and i not in self._requested_pieces and i not in self._downloaded_pieces:
                await self._request_piece(i)
                self._requested_pieces.add(i)
                if len(self._requested_pieces) >= 5:
                    break

    async def _request_piece(self, piece_index):
        piece_length = self._torrent.bytes_count_per_piece
        if piece_index == self._torrent.pieces_count - 1:
            piece_length = self._torrent.size % self._torrent.bytes_count_per_piece

        self._in_progress_pieces[piece_index] = {}

        for offset in range(0, piece_length, BLOCK_SIZE):
            length = min(BLOCK_SIZE, piece_length - offset)
            request = await self._generate_request(length, offset, piece_index)
            await self._send(request)

    async def _handle_piece(self, piece_data):
        index = int.from_bytes(piece_data[:4], byteorder='big')
        begin = int.from_bytes(piece_data[4:8], byteorder='big')
        block = piece_data[8:]
        logger.debug(f"Received piece {index}, offset {begin}, length {len(block)}")

        if index not in self._in_progress_pieces:
            self._in_progress_pieces[index] = {}
        self._in_progress_pieces[index][begin] = block

        if sum(len(block) for block in
               self._in_progress_pieces[index].values()) >= self._torrent.bytes_count_per_piece:
            complete_piece = b''.join(block for _, block in sorted(self._in_progress_pieces[index].items()))
            if self._verify_piece(index, complete_piece):
                logger.info(f"Piece {index} downloaded and verified")
                await self._file_saver.save_piece(index, complete_piece)
                self._requested_pieces.remove(index)
                self._downloaded_pieces.add(index)
                del self._in_progress_pieces[index]
                await self._request_pieces()
            else:
                logger.error(f"Piece {index} failed verification")
                del self._in_progress_pieces[index]
                self._requested_pieces.remove(index)
                await self._request_pieces()

    def _verify_piece(self, index, piece_data):
        piece_hash = hashlib.sha1(piece_data).digest()
        return piece_hash == self._torrent.get_piece_hash(index)

    async def _send_interested_message(self):
        interested_message = b"\0\0\0\1\2"  # 4 байта длина сообщения, 5-ый байт - код сообщения
        logger.debug(f"Sending message: Interested")
        await self._send(interested_message)

    async def _receive(self, n):
        try:
            data = await self._reader.readexactly(n)
            logger.debug(f"Read: Received {n} bytes from {self._ip}:{self._port}")
            return data
        except asyncio.IncompleteReadError as e:
            logger.error(f"Incomplete read error: expected {n} bytes, but got {len(e.partial)} bytes")
            return e.partial
        except Exception as e:
            logger.error(f"Failed to read {n} bytes, reason: {str(e)}")
            return b""

    async def _send(self, data):
        self._writer.write(data)
        logger.debug(f"Sending data to {self._ip}:{self._port}")
        await self._writer.drain()

    @staticmethod
    async def _generate_request(length, offset, piece_index):
        return ((13).to_bytes(4, byteorder='big')
                + bytes([MessageType.REQUEST])
                + piece_index.to_bytes(4, byteorder='big')
                + offset.to_bytes(4, byteorder='big')
                + length.to_bytes(4, byteorder='big'))

    def _generate_handshake(self) -> bytes:
        """Returns generated handshake for first request with peer."""
        return b"".join([chr(19).encode(),
                         b"BitTorrent protocol",
                         b"\0" * 8,
                         self._torrent.info_hash(),
                         self._peer_id.encode()])
