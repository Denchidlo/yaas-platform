import wave as wv
import numpy as np
from typing import BinaryIO, Union

from pyyaap.codec.decode.providers.base import BaseCodec
from pyyaap.codec.decode.utils import Record


class WAVCodec(BaseCodec):
    SUPPORTED_FORMATS = [
        "wav"
    ]

    @classmethod
    def _read_record(cls, file: Union[str, BinaryIO], ext=None, limit=1000):
        with wv.open(file) as wav:
            params = wav.getparams()
            data = wav.readframes(
                params.nframes
            )

        n_channels = params.nchannels
        f_width = params.sampwidth
        n_samples, r = divmod(len(data), n_channels * f_width)

        assert r == 0, "Wav file corrupted"

        if f_width != 3:
            sign_type = 'u' if f_width == 1 else 'i'
            pcm_signal = np.frombuffer(data, dtype=f'<{sign_type}{f_width}').reshape(-1, n_channels)
        else:
            wav_transformed = np.empty((n_samples, n_channels, 4), dtype=np.int8)
            wav_raw = np.frombuffer(data, dtype=np.int8)
            wav_transformed[:,:,:f_width] = wav_raw.reshape(-1, n_channels, f_width)
            # Expand carry bit to MSB
            wav_transformed[:,:,-1] = (wav_transformed[:,:, f_width - 1] >> 7) * 255 
            pcm_signal = wav_transformed.reshape(-1, n_channels)

        if limit:
            pcm_signal = pcm_signal[:limit * 1000,:]

        return [ch.flatten() for ch in np.split(pcm_signal, pcm_signal.shape[-1], axis=-1)], params.framerate
