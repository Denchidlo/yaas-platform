from hashlib import sha1
from collections import namedtuple
import numpy as np


Record = namedtuple("Record", [
    "channels", "framerate", "name", "hash"
])

HASHING_BLOCK_SIZE = 2**20

def compute_binary_hash(fd):
    global HASHING_BLOCK_SIZE

    sha_signature = sha1()

    if isinstance(fd, str):
        fd = open(fd, 'rb')

    fd.seek(0)
    while True:
        buf = fd.read(HASHING_BLOCK_SIZE)
        if not buf:
            break
        sha_signature.update(buf)
    fd.seek(0)

    return sha_signature.hexdigest().upper()
