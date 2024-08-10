import random
import string


class Peer:
    def __init__(self):
        self.peer_id = self.generate_peer_id()

    @staticmethod
    def generate_peer_id():
        return "FIIT-" + ''.join(random.choices(string.ascii_letters + string.digits, k=15))

    def __str__(self):
        return self.peer_id
