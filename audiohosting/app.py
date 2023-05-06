import os
import re

import aiohttp_cors
from aiohttp import web

from utils import get_chunk
from config import (
    RAW_AUDIO_DIRECTORY_PATH, 
    PROCESSED_AUDIO_EXTENSIONS,
    PROCESSED_AUDIO_DIRECTORY_PATH,
)


routes = web.RouteTableDef()

@routes.get('/')
async def root(request):
    return web.Response(text='YaAS Audio Straming Service')


@routes.post('/upload/audio')
async def upload(request):
    print('upload...')
    reader = await request.multipart()
    field = await reader.next()
    filename = field.filename

    size = 0
    with open(os.path.join(RAW_AUDIO_DIRECTORY_PATH, filename), 'wb') as f:
        while True:
            chunk = await field.read_chunk()  # 8192 bytes by default.
            if not chunk:
                break
            size += len(chunk)
            f.write(chunk)
    
    print('finished upload')
    return web.Response(text='{} sized of {} successfully stored'
                             ''.format(filename, size))


@routes.get('/audio/{filename}')
async def get_streaming_audio(request):
    filename = request.match_info['filename']
    print(f'GET /audio/{filename}')
    ext = filename.split('.')[-1]

    assert ext in PROCESSED_AUDIO_EXTENSIONS, f"Unsupported extension: {ext} in {filename}"

    filename = os.path.join(PROCESSED_AUDIO_DIRECTORY_PATH, filename)
    range_header = request.headers.get('Range', None)
    l_ptr, r_ptr = 0, None
    if range_header:
        match = re.search(r'(\d+)-(\d*)', range_header)
        groups = match.groups()

        if groups[0]:
            l_ptr = int(groups[0])
        if groups[1]:
            r_ptr = int(groups[1])
       
    chunk, start, length, file_size = await get_chunk(filename, l_ptr, r_ptr)
    headers = {}
    headers['Accept-Ranges'] = 'bytes'
    headers['Cache-Control'] = 'no-cache'
    headers['Content-Range'] = 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size)

    return web.Response(body=chunk, status=206, content_type=f'audio/{ext}', headers=headers)


app = web.Application()
app.add_routes(routes)


cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
})

# Configure CORS on all routes.
for route in list(app.router.routes()):
    cors.add(route)


if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8888)
