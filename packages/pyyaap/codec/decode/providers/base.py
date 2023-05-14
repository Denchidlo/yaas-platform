from typing import BinaryIO, Union

from pyyaap.codec.decode.utils import Record, compute_binary_hash


class BaseCodec:
    SUPPORTED_FORMATS = []

    @classmethod
    def read(cls, file: Union[str, BinaryIO], ext=None, limit=1000) -> Record:
        if isinstance(file, str):
            ext = file.split(".")[-1]
            fd = open(file, "rb")
        else:
            fd = file
        
        sha_signature = compute_binary_hash(fd)
        
        channels, framerate = cls._read_record(fd, ext, limit)

        fd.seek(0)
        if isinstance(file, str):
            fd.close()

        return Record(
            channels=channels, 
            framerate=framerate, 
            name=f"unk-audio__{sha_signature}" if not isinstance(file, str) else file, 
            hash=sha_signature
        )
