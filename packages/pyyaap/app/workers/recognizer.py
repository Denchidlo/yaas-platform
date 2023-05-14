import os
import sys
import traceback
import numpy as np
from itertools import groupby
from time import time
from typing import Dict, List, Tuple


import pyyaap.codec.decode as decoder
from pyyaap.matching.signal.fingerprint import fingerprint
from pyyaap.app.core.db import BaseDatabase
from pyyaap.config.app import (
    FIELD_FILE_SHA1, FIELD_TOTAL_HASHES, 
    FINGERPRINTED_CONFIDENCE,FINGERPRINTED_HASHES, 
    HASHES_MATCHED, INPUT_CONFIDENCE, INPUT_HASHES, 
    OFFSET, OFFSET_SECS, AUDIO_ID, AUDIO_NAME, TOPN, TOTAL_TIME, 
    FINGERPRINT_TIME, QUERY_TIME, ALIGN_TIME, RESULTS
)
from pyyaap.config.fingerprint import (
    FP_SPEC_FREQ, FP_SPEC_OVERLAP, FP_SPEC_WIN_SIZE
)


class AudioRecognizer:    
    def __init__(self, config: Dict, db: BaseDatabase):
        self.config= config
        self.db = db

        self.limit = None

    def generate_fingerprints(self, samples: np.ndarray, Fs=FP_SPEC_FREQ) -> Tuple[List[Tuple[str, int]], float]:
        f"""
            Generate the fingerprints for the given sample data (channel).
            :param samples: numpy array represents the channel info of the given audio file.
            :return: a list of tuples for hash and its corresponding offset, together with the generation time.
        """
        t = time()
        hashes = fingerprint(samples, **{**self.config, 'freq':Fs})
        fingerprint_time = time() - t
        return hashes, fingerprint_time

    def find_matches(self, hashes: List[Tuple[str, int]]) -> Tuple[List[Tuple[int, int]], Dict[str, int], float]:
        """
        Finds the corresponding matches on the fingerprinted audios for the given hashes.
        :param hashes: list of tuples for hashes and their corresponding offsets
        :return: a tuple containing the matches found against the db, a dictionary which counts the different
         hashes matched for each audio (with the audio id as key), and the time that the query took.
        """
        t = time()
        matches, dedup_hashes = self.db.return_matches(hashes)
        query_time = time() - t

        return matches, dedup_hashes, query_time

    def align_matches(self, matches: List[Tuple[int, int]], dedup_hashes: Dict[str, int], queried_hashes: int,
                      topn: int = TOPN) -> List[Dict[str, any]]:
        """
        Finds hash matches that align in time with other matches and finds
        consensus about which hashes are "true" signal from the audio.
        :param matches: matches from the database
        :param dedup_hashes: dictionary containing the hashes matched without duplicates for each audio
        (key is the audio id).
        :param queried_hashes: amount of hashes sent for matching against the db
        :param topn: number of results being returned back.
        :return: a list of dictionaries (based on topn) with match information.
        """
        # count offset occurrences per audio and keep only the maximum ones.
        sorted_matches = sorted(matches, key=lambda m: (m[0], m[1]))
        counts = [(*key, len(list(group))) for key, group in groupby(sorted_matches, key=lambda m: (m[0], m[1]))]
        audios_matches = sorted(
            [max(list(group), key=lambda g: g[2]) for key, group in groupby(counts, key=lambda count: count[0])],
            key=lambda count: count[2], reverse=True
        )

        audios_result = []
        for audio_id, offset, _ in audios_matches[0:topn]:  # consider topn elements in the result
            audio = self.db.get_audio_by_id(audio_id)

            audio_name = audio.get(AUDIO_NAME, None)
            audio_hashes = audio.get(FIELD_TOTAL_HASHES, None)
            nseconds = round(float(offset) / FP_SPEC_FREQ * FP_SPEC_WIN_SIZE * FP_SPEC_OVERLAP, 5)
            hashes_matched = dedup_hashes[audio_id]

            audio = {
                AUDIO_ID: str(audio_id),
                AUDIO_NAME: str(audio_name),
                # INPUT_HASHES: queried_hashes,
                # FINGERPRINTED_HASHES: audio_hashes,
                # HASHES_MATCHED: hashes_matched,
                # Percentage regarding hashes matched vs hashes from the input.
                INPUT_CONFIDENCE: round(hashes_matched / queried_hashes, 2),
                # Percentage regarding hashes matched vs hashes fingerprinted in the db.
                FINGERPRINTED_CONFIDENCE: round(hashes_matched / audio_hashes, 2),
                # OFFSET: offset,
                # OFFSET_SECS: nseconds,
                # FIELD_FILE_SHA1: audio.get(FIELD_FILE_SHA1, None).encode("utf8")
            }

            audios_result.append(audio)

        return audios_result

    def _recognize(self, *data, freq=FP_SPEC_FREQ) -> Tuple[List[Dict[str, any]], int, int, int]:
        fingerprint_times = []
        hashes = set()  # to remove possible duplicated fingerprints we built a set.
        for channel in data:
            fingerprints, fingerprint_time = self.generate_fingerprints(channel, Fs=freq)
            fingerprint_times.append(fingerprint_time)
            hashes |= set(fingerprints)

        matches, dedup_hashes, query_time = self.find_matches(hashes)

        t = time()
        final_results = self.align_matches(matches, dedup_hashes, len(hashes))
        align_time = time() - t

        return final_results, np.sum(fingerprint_times), query_time, align_time

    def recognize(self, type, **payload) -> Dict[str, any]:
        framerate = FP_SPEC_FREQ
        if type == 'file':
            record = decoder.read_file(payload["payload"], self.limit, ext=payload['ext'])
            channels = record.channels
            framerate = record.framerate
        else:
            channels = payload['channels']        

        t = time()
        matches, fingerprint_time, query_time, align_time = self._recognize(*channels, freq=framerate)
        t = time() - t

        results = {
            TOTAL_TIME: t,
            FINGERPRINT_TIME: fingerprint_time,
            QUERY_TIME: query_time,
            ALIGN_TIME: align_time,
            RESULTS: matches
        }

        return results
