import os
import re
import tempfile
import aiohttp
import aiohttp_cors
import aiohttp_swagger3
from aiohttp import web
from typing import Dict, List, Tuple

from pyyaap.utils import get_chunk, get_connection
import pyyaap.codec.decode as audio_codec
from pyyaap.app.core.db import PostgreSQLDatabase
from pyyaap.app.workers import AudioRecognizer
from config import (
    RAW_AUDIO_DIRECTORY_PATH, 
    PROCESSED_AUDIO_EXTENSIONS,
    PROCESSED_AUDIO_DIRECTORY_PATH,
)


routes = web.RouteTableDef()

RECOGNIZER_CFG = {  }
DB_CONNECTOR = PostgreSQLDatabase(
    **get_connection()
)
recognizer = AudioRecognizer(RECOGNIZER_CFG, DB_CONNECTOR)


@routes.get('/')
async def root(request):
    return web.Response(text='YaAS Audio Search Service')


# @routes.post('/recognize')
async def recognize(request: web.Request) -> web.Response:
    """
    Method receiving multipart form as POST to upload big file

    :param request: Aiohttp request object
    :type request: aiohttp.web.Request
    :returns: Aiohttp response object
    :type: aiohttp.web.Response
    ---
    summary: Upload file with multiparts form
    tags:
        - upload
    requestBody:
        content:
            multipart/form-data:
                schema:
                    type: object
                    properties:
                        name:
                            type: string
                            description: Name of the file uploaded
                            example: ISO CentOS 7
                        payload:
                            type: string
                            format: binary
    responses:
        '201':
            description: Recognition best candidate
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            total_time:
                                type: integer
                                description: Total search time (ms)
                                example: 5
                            fingeprint_time:
                                type: integer
                                description: Fingerprint creation time (ms)
                                example: 5
                            query_time:
                                type: integer
                                description: DB execution query time (ms)
                                example: 5
                            align_time:
                                type: integer
                                description: Candidate selection query time (ms)
                                example: 5
                            results:
                                type: array
                                items:
                                    type: object
    """
    print('upload...')
    # https://docs.aiohttp.org/en/stable/web_quickstart.html#file-uploads
    reader = await request.multipart()

    field = await reader.next()
    assert field.name == "name", 'First form field must be a "name" field containing string'
    name = str(await field.read(), "utf-8")

    field = await reader.next()
    assert field.name == "payload", 'Second form field must be "payload" field containing file bytes'
    filename = field.filename

    size = 0
    with tempfile.NamedTemporaryFile() as tmp:
        while True or size < 2:
            chunk = await field.read_chunk()  # 8192 bytes by default.
            if not chunk:
                break
            size += tmp.write(chunk)

        with open(tmp.name, 'rb') as buff:
            results = recognizer.recognize(type='file', payload=buff, ext=name.split('.')[-1])
    
    return web.json_response(results)


if __name__ == '__main__':
    MAX_FILE_SIZE = 1e9

    app = web.Application()
    app.add_routes(routes)

    # Configure CORS on all routes.
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
    })
    for route in list(app.router.routes()):
        cors.add(route)
      
    swagger = aiohttp_swagger3.SwaggerDocs(app, 
        validate=False, swagger_ui_settings=aiohttp_swagger3.SwaggerUiSettings(path="/docs/"),
        info=aiohttp_swagger3.SwaggerInfo(
            title="yaas searching engine",
            version="1.0.0",
        ),)

    async def passthru_handler(request: aiohttp.web.Request) -> Tuple[aiohttp.web.Request, bool]:
        return request, True

    swagger.register_media_type_handler("multipart/form-data", passthru_handler)
    swagger.add_routes([aiohttp.web.post("/recognize", recognize)])

    web.run_app(app, host='0.0.0.0', port=8888)
