import os
import logging

from pyyaap.app.core.db import PostgreSQLDatabase
from pyyaap.app.workers import FingerpintCrawler
import pyyaap.codec.decode as audio_codec
from pyyaap.config.app import SUPPORTED_EXTENSIONS


CRAWLER_CFG = {}
TARGET_DIR = '/audio/raw'


def get_connection():
    return {
        'database': os.getenv('POSTGRES_DB'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'host': os.getenv('POSTGRES_HOST'),
        'port': os.getenv('POSTGRES_PORT'),
    }

def run_crawling_session():
    sql_connection = get_connection()
    
    db = PostgreSQLDatabase(**sql_connection)
    crawler = FingerpintCrawler(CRAWLER_CFG, db)

    n_audio = 0

    try:
        db.empty()
        db.delete_unfingerprinted_songs()
        n_audio = db.get_num_songs()
    except:
        logging.info("Non-initialized database: apply DDL")
        db.setup()
    
    n_stored_audio = len(audio_codec.find_files(TARGET_DIR, SUPPORTED_EXTENSIONS))

    if n_stored_audio > n_audio: 
        logging.info(
            f'Started crawling session: {n_stored_audio - n_audio} files to parse'
        )
        crawler.fingerprint_directory(
            path=TARGET_DIR, extensions=SUPPORTED_EXTENSIONS,
            nprocesses=None
        )
    elif n_stored_audio < n_audio:
        logging.critical(
            f'File storage corruption! Expected maximal audio in index: {n_stored_audio}, got: {n_audio}'
        )
        db.empty()
        crawler.fingerprint_directory(
            path=TARGET_DIR, extensions=FP_SUPPORTED_EXTENSIONS,
            nprocesses=None
        )
    else:
        pass

    
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO, filename="crawler_session.log",
        filemode="w", format="%(asctime)s - %(levelname)s - %(message)s"
    )

    run_crawling_session()
