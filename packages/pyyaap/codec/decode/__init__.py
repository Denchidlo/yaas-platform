import os
import fnmatch
from typing import Dict, List, Tuple

from pyyaap.codec.decode.providers import (
    PyDubCodec, WAVCodec
)
from pyyaap.codec.decode.utils import Record, compute_binary_hash


REGISTERED_CODECS = [
    WAVCodec, PyDubCodec 
]

def read_file(file: str, limit=1000, ext=None) -> Record:
    if isinstance(file, str):
        ext = file.split('.')[-1]
        f = open(file, 'rb')
    else:
        f = file

    record = None
    for codec in REGISTERED_CODECS:
        if ext in codec.SUPPORTED_FORMATS:
            record = codec.read(f, ext=ext, limit=limit)

    if isinstance(file, str):
        f.close()

    if record is None:
        raise ValueError("Unsupported audio format encountered")

    return record

def find_files(path: str, extensions: List[str]) -> List[Tuple[str, str]]:
    """
    Get all files that meet the specified extensions.
    :param path: path to a directory with audio files.
    :param extensions: file extensions to look for.
    :return: a list of tuples with file name and its extension.
    """
    # Allow both with ".mp3" and without "mp3" to be used for extensions
    extensions = [e.replace(".", "") for e in extensions]

    results = []
    for dirpath, dirnames, files in os.walk(path):
        for extension in extensions:
            for f in fnmatch.filter(files, f"*.{extension}"):
                p = os.path.join(dirpath, f)
                results.append((p, extension))
    return results

def get_audio_name_from_path(file_path: str) -> str:
    """
    Extracts song name from a file path.
    :param file_path: path to an audio file.
    :return: file name
    """
    return os.path.splitext(os.path.basename(file_path))[0]
