import os
import sys
import traceback
import logging
import multiprocessing
from itertools import groupby
from time import time
from typing import Dict, List, Tuple

import pyyaap.codec.decode as audio_codec
from pyyaap.matching.signal.fingerprint import fingerprint

from pyyaap.app.core.db import BaseDatabase
from pyyaap.config.app import (
    FIELD_FILE_SHA1, AUDIO_NAME, TOPN
)


class FingerpintCrawler:
    def __init__(self, config: Dict, db: BaseDatabase):
        self.config = config
        self.db = db

        # if we should limit seconds fingerprinted,
        # None|-1 means use entire track
        self.limit = self.config.get("fingerprint_limit", None)
        if self.limit == -1:  # for JSON compatibility
            self.limit = None

    def __load_fingerprinted_audio_hashes(self) -> None:
        # get audios previously indexed
        self.audios = self.db.get_audios()
        self.audiohashes_set = set()  # to know which ones we've computed before
        for audio in self.audios:
            audio_hash = audio[FIELD_FILE_SHA1]
            self.audiohashes_set.add(audio_hash)

    def get_fingerprinted_audios(self) -> List[Dict[str, any]]:
        return self.db.get_audios()

    def delete_audios_by_id(self, audio_ids: List[int]) -> None:
        self.db.delete_audios_by_id(audio_ids)

    def fingerprint_directory(self, path: str, extensions: str, nprocesses: int = None) -> None:
        """
        Given a directory and a set of extensions it fingerprints all files that match each extension specified.
        :param path: path to the directory.
        :param extensions: list of file extensions to consider.
        :param nprocesses: amount of processes to fingerprint the files within the directory.
        """
        # Try to use the maximum amount of processes if not given.
        self.__load_fingerprinted_audio_hashes()
        
        try:
            nprocesses = nprocesses or multiprocessing.cpu_count()
        except NotImplementedError:
            nprocesses = 1
        else:
            nprocesses = 1 if nprocesses <= 0 else nprocesses

        pool = multiprocessing.Pool(nprocesses)

        filenames_to_fingerprint = []
        for filename, ext in audio_codec.find_files(path, extensions):
            # don't refingerprint already fingerprinted files
            if audio_codec.compute_binary_hash(filename) in self.audiohashes_set:
                logging.info(f"{filename} already fingerprinted, continuing...")
                continue

            filenames_to_fingerprint.append(filename)

        # Prepare _fingerprint_worker input
        worker_input = list(zip(filenames_to_fingerprint, [self.limit] * len(filenames_to_fingerprint)))

        # Send off our tasks
        iterator = pool.imap_unordered(FingerpintCrawler._fingerprint_worker, worker_input)

        # Loop till we have all of them
        while True:
            try:
                audio_name, extension, hashes, file_hash = next(iterator)
            except multiprocessing.TimeoutError:
                continue
            except StopIteration:
                break
            except Exception:
                logging.info("Failed fingerprinting")
                # logging.info traceback because we can't reraise it here
                traceback.print_exc(file=sys.stdout)
            else:
                sid = self.db.insert_audio(
                    audio_name + extension, file_hash, len(hashes)
                )

                self.db.insert_hashes(sid, hashes)
                self.db.set_audio_fingerprinted(sid)
                self.__load_fingerprinted_audio_hashes()

        pool.close()
        pool.join()

    @staticmethod
    def _fingerprint_worker(arguments):
        # Pool.imap sends arguments as tuples so we have to unpack
        # them ourself.
        try:
            file_name, limit = arguments
        except ValueError:
            pass

        audio_name, extension = os.path.splitext(os.path.basename(file_name))

        fingerprints, file_hash = FingerpintCrawler.get_file_fingerprints(file_name, limit, print_output=True)

        return audio_name, extension, fingerprints, file_hash

    @staticmethod
    def get_file_fingerprints(file_name: str, limit: int, print_output: bool = False):
        channels, framerate, _, file_hash = audio_codec.read_file(file_name, limit)
        
        fingerprints = set()
        channel_amount = len(channels)
        for channeln, channel in enumerate(channels, start=1):
            if print_output:
                logging.info(f"Fingerprinting channel {channeln}/{channel_amount} for {file_name}")

            hashes = fingerprint(channel, freq=framerate)

            if print_output:
                logging.info(f"Finished channel {channeln}/{channel_amount} for {file_name}")

            fingerprints |= set(hashes)

        return fingerprints, file_hash
