import random
import string


def generate_peer_id() -> str:
    """Returns randomly generated peer id in format with prefix '-FIIT-'."""
    return "-FIIT-" + ''.join(random.choices(string.ascii_letters + string.digits, k=14))
