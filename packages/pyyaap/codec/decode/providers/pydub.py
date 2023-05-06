import numpy as np
from pydub import AudioSegment
from typing import BinaryIO, Union

from pyyaap.codec.decode.providers.base import BaseCodec
from pyyaap.codec.decode.utils import Record


class PyDubCodec(BaseCodec):
    SUPPORTED_FORMATS = [
        "mp3", "ogg"
    ]

    @classmethod
    def _read_record(cls, file: Union[str, BinaryIO], ext=None, limit=1000) -> Record:
        pcm_signal = AudioSegment.from_file(file)

        if limit:
            pcm_signal = pcm_signal[:limit * 1000]

        assert pcm_signal.frame_rate == 44100, "Only 44.1 kHz audio is supported"
        data = np.fromstring(pcm_signal.raw_data, np.int16)
        n_ch = pcm_signal.channels
        
        if limit:
            data = data[:n_ch * limit * 1000]

        channels = []
        for ch in range(n_ch):
            channels.append(data[ch::n_ch])

        return channels, pcm_signal.frame_rate
