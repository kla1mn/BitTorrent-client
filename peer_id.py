import random
import string
import logging

from config import LOGGING_LEVEL

logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)


class PeerId:
    def __init__(self):
        self.peer_id = self.generate_peer_id()
        logger.debug("PeerId generated")

    @staticmethod
    def generate_peer_id() -> str:
        """Returns randomly generated peer id in format with prefix 'FIIT-'."""
        return "FIIT-" + ''.join(random.choices(string.ascii_letters + string.digits, k=15))

    def __str__(self):
        return self.peer_id
