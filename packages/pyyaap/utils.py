import os
import aiofile


def get_connection():
    return {
        'database': os.getenv('POSTGRES_DB'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'host': os.getenv('POSTGRES_HOST'),
        'port': os.getenv('POSTGRES_PORT'),
    }

async def get_chunk(filename, l_ptr=None, r_ptr=None):
    file_size = os.stat(filename).st_size
    default_chunk_size = 8192
    start = 0
    
    if l_ptr < file_size:
        start = l_ptr
    if r_ptr:
        length = r_ptr + 1 - l_ptr
    else:
        length = min(default_chunk_size, file_size - start)

    async with aiofile.async_open(filename, 'rb') as f:
        f.seek(start)
        chunk = await f.read(length)
    return chunk, start, length, file_size
 