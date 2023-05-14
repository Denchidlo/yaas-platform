import queue

import psycopg2
from psycopg2.extras import DictCursor

from pyyaap.app.core.db.base import CommonDatabase
from pyyaap.config.app import (FIELD_FILE_SHA1, FIELD_FINGERPRINTED,
                                    FIELD_HASH, FIELD_OFFSET, FIELD_AUDIO_ID,
                                    FIELD_AUDIONAME, FIELD_TOTAL_HASHES,
                                    FINGERPRINTS_TABLENAME, AUDIOS_TABLENAME)


class PostgreSQLDatabase(CommonDatabase):
    type = "postgres"

    # CREATES
    CREATE_AUDIOS_TABLE = f"""
        CREATE TABLE IF NOT EXISTS "{AUDIOS_TABLENAME}" (
            "{FIELD_AUDIO_ID}" SERIAL
        ,   "{FIELD_AUDIONAME}" VARCHAR(250) NOT NULL
        ,   "{FIELD_FINGERPRINTED}" SMALLINT DEFAULT 0
        ,   "{FIELD_FILE_SHA1}" BYTEA
        ,   "{FIELD_TOTAL_HASHES}" INT NOT NULL DEFAULT 0
        ,   "dt_created" TIMESTAMP NOT NULL DEFAULT now()
        ,   "dt_modified" TIMESTAMP NOT NULL DEFAULT now()
        ,   CONSTRAINT "pk_{AUDIOS_TABLENAME}_{FIELD_AUDIO_ID}" PRIMARY KEY ("{FIELD_AUDIO_ID}")
        ,   CONSTRAINT "uq_{AUDIOS_TABLENAME}_{FIELD_AUDIO_ID}" UNIQUE ("{FIELD_AUDIO_ID}")
        );
    """

    CREATE_FINGERPRINTS_TABLE = f"""
        CREATE TABLE IF NOT EXISTS "{FINGERPRINTS_TABLENAME}" (
            "{FIELD_HASH}" BIGINT NOT NULL
        ,   "audio_{FIELD_AUDIO_ID}" INT NOT NULL
        ,   "{FIELD_OFFSET}" INT NOT NULL
        ,   CONSTRAINT "fk_{FINGERPRINTS_TABLENAME}_audio_{FIELD_AUDIO_ID}" FOREIGN KEY ("audio_{FIELD_AUDIO_ID}")
                REFERENCES "{AUDIOS_TABLENAME}"("{FIELD_AUDIO_ID}") ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS "ix_{FINGERPRINTS_TABLENAME}_{FIELD_HASH}" ON "{FINGERPRINTS_TABLENAME}"
        USING hash ("{FIELD_HASH}");
    """

    CREATE_FINGERPRINTS_TABLE_INDEX = f"""
        CREATE INDEX "ix_{FINGERPRINTS_TABLENAME}_{FIELD_HASH}" ON "{FINGERPRINTS_TABLENAME}"
        USING hash ("{FIELD_HASH}");
    """

    # INSERTS (IGNORES DUPLICATES)
    INSERT_FINGERPRINT = f"""
        INSERT INTO "{FINGERPRINTS_TABLENAME}" (
                "audio_{FIELD_AUDIO_ID}"
            ,   "{FIELD_HASH}"
            ,   "{FIELD_OFFSET}")
        VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;
    """

    INSERT_AUDIO = f"""
        INSERT INTO "{AUDIOS_TABLENAME}" ("{FIELD_AUDIONAME}", "{FIELD_FILE_SHA1}","{FIELD_TOTAL_HASHES}")
        VALUES (%s, decode(%s, 'hex'), %s)
        RETURNING "{FIELD_AUDIO_ID}";
    """

    # SELECTS
    SELECT = f"""
        SELECT "audio_{FIELD_AUDIO_ID}", "{FIELD_OFFSET}"
        FROM "{FINGERPRINTS_TABLENAME}"
        WHERE "{FIELD_HASH}" = %s;
    """

    SELECT_MULTIPLE = f"""
        SELECT "{FIELD_HASH}", "audio_{FIELD_AUDIO_ID}", "{FIELD_OFFSET}"
        FROM "{FINGERPRINTS_TABLENAME}"
        WHERE "{FIELD_HASH}" IN (%s);
    """

    SELECT_ALL = f'SELECT "audio_{FIELD_AUDIO_ID}", "{FIELD_OFFSET}" FROM "{FINGERPRINTS_TABLENAME}";'

    SELECT_AUDIO = f"""
        SELECT
            "{FIELD_AUDIONAME}"
        ,   upper(encode("{FIELD_FILE_SHA1}", 'hex')) AS "{FIELD_FILE_SHA1}"
        ,   "{FIELD_TOTAL_HASHES}"
        FROM "{AUDIOS_TABLENAME}"
        WHERE "{FIELD_AUDIO_ID}" = %s;
    """

    SELECT_NUM_FINGERPRINTS = f'SELECT COUNT(*) AS n FROM "{FINGERPRINTS_TABLENAME}";'

    SELECT_UNIQUE_AUDIO_IDS = f"""
        SELECT COUNT("{FIELD_AUDIO_ID}") AS n
        FROM "{AUDIOS_TABLENAME}"
        WHERE "{FIELD_FINGERPRINTED}" = 1;
    """

    SELECT_AUDIOS = f"""
        SELECT
            "{FIELD_AUDIO_ID}"
        ,   "{FIELD_AUDIONAME}"
        ,   upper(encode("{FIELD_FILE_SHA1}", 'hex')) AS "{FIELD_FILE_SHA1}"
        ,   "{FIELD_TOTAL_HASHES}"
        ,   "dt_created"
        FROM "{AUDIOS_TABLENAME}"
        WHERE "{FIELD_FINGERPRINTED}" = 1;
    """

    # DROPS
    DROP_FINGERPRINTS = F'DROP TABLE IF EXISTS "{FINGERPRINTS_TABLENAME}";'
    DROP_AUDIOS = F'DROP TABLE IF EXISTS "{AUDIOS_TABLENAME}";'

    # UPDATE
    UPDATE_AUDIO_FINGERPRINTED = f"""
        UPDATE "{AUDIOS_TABLENAME}" SET
            "{FIELD_FINGERPRINTED}" = 1
        ,   "dt_modified" = now()
        WHERE "{FIELD_AUDIO_ID}" = %s;
    """

    # DELETES
    DELETE_UNFINGERPRINTED = f"""
        DELETE FROM "{AUDIOS_TABLENAME}" WHERE "{FIELD_FINGERPRINTED}" = 0;
    """

    DELETE_AUDIOS = f"""
        DELETE FROM "{AUDIOS_TABLENAME}" WHERE "{FIELD_AUDIO_ID}" IN (%s);
    """

    # IN
    IN_MATCH = "%s"

    def __init__(self, **options):
        super().__init__()
        self.cursor = cursor_factory(**options)
        self._options = options

    def after_fork(self) -> None:
        # Clear the cursor cache, we don't want any stale connections from
        # the previous process.
        Cursor.clear_cache()

    def insert_audio(self, audio_name: str, file_hash: str, total_hashes: int) -> int:
        """
        Inserts a audio name into the database, returns the new
        identifier of the audio.
        :param audio_name: The name of the audio.
        :param file_hash: Hash from the fingerprinted file.
        :param total_hashes: amount of hashes to be inserted on fingerprint table.
        :return: the inserted id.
        """
        with self.cursor() as cur:
            cur.execute(self.INSERT_AUDIO, (audio_name, file_hash, total_hashes))
            return cur.fetchone()[0]

    def __getstate__(self):
        return self._options,

    def __setstate__(self, state):
        self._options, = state
        self.cursor = cursor_factory(**self._options)


def cursor_factory(**factory_options):
    def cursor(**options):
        options.update(factory_options)
        return Cursor(**options)
    return cursor


class Cursor(object):
    """
    Establishes a connection to the database and returns an open cursor.
    # Use as context manager
    with Cursor() as cur:
        cur.execute(query)
        ...
    """
    def __init__(self, dictionary=False, **options):
        super().__init__()

        self._cache = queue.Queue(maxsize=5)

        try:
            conn = self._cache.get_nowait()
            # Ping the connection before using it from the cache.
            conn.ping(True)
        except queue.Empty:
            conn = psycopg2.connect(**options)

        self.conn = conn
        self.dictionary = dictionary

    @classmethod
    def clear_cache(cls):
        cls._cache = queue.Queue(maxsize=5)

    def __enter__(self):
        if self.dictionary:
            self.cursor = self.conn.cursor(cursor_factory=DictCursor)
        else:
            self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, extype, exvalue, traceback):
        # if we had a PostgreSQL related error we try to rollback the cursor.
        if extype is psycopg2.DatabaseError:
            self.cursor.rollback()

        self.cursor.close()
        self.conn.commit()

        # Put it back on the queue
        try:
            self._cache.put_nowait(self.conn)
        except queue.Full:
            self.conn.close()