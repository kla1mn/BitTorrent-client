import random
import string


def generate_peer_id():
    return "FIIT-" + ''.join(random.choices(string.ascii_letters + string.digits, k=15))
