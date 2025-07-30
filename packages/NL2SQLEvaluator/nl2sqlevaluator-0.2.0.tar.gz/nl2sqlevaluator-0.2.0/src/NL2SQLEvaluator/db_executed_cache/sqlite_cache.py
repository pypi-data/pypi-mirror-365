import hashlib
import logging
import pickle
from typing import Optional

import sqlalchemy
from sqlalchemy import Column, String, LargeBinary, Text, insert, select, create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Session

from NL2SQLEvaluator.logger import get_logger


def hash_db_id_sql(db_id, query) -> str:
    value = f"{db_id}|{query}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class Base(DeclarativeBase):
    pass


class CachedData(Base):
    __tablename__ = "cache_data"

    hash_key = Column(String(64), primary_key=True, index=True)
    db_id = Column(String(1500), nullable=False)
    query = Column(Text, nullable=False)
    result = Column(LargeBinary, nullable=True)

    def __repr__(self):
        return f"CachedData(hash_key={self.hash_key!r}, db_id={self.db_id!r}, query={self.query!r}, result={self.result!r})"


class SQLiteCache:
    def __init__(
            self,
            engine,
            logger: Optional[logging.Logger] = None,
            timeout: Optional[int | float] = 100,
            *args,
            **kwargs,
    ):
        self.timeout = timeout
        self.engine = engine
        Base.metadata.create_all(engine)
        self.logger = logger or get_logger(name=__name__, level="INFO")
        self.engine_url = str(engine.url)

    @classmethod
    def from_uri(cls, *args, **kwargs) -> Optional["SQLiteCache"]:
        db_path = kwargs.get("db_path", "cache.sqlite")
        logger = kwargs.get("logger", get_logger(name=__name__, level="ERROR"))
        timeout = kwargs.get("timeout", 100)
        url = f"sqlite:///{db_path}"
        logger.info(
            f"Connecting to SQLite database for cache uri: `{url}`, timeout: {timeout} seconds"
        )
        try:
            return cls(
                engine=create_engine(
                    url,
                    connect_args={"timeout": timeout},
                    echo=kwargs.get("is_echo", False),
                ),
                logger=logger,
            )
        except sqlalchemy.exc.OperationalError as e:
            logger.error(
                f"Failed to connect to SQLite database: {url}, returning None. Error: {e}"
            )
            return None

    def get_from_cache(self, db_id, query: str) -> list[tuple] | None:
        hash_id = hash_db_id_sql(db_id, query)
        self.logger.debug(f"Fetching from cache with hash_id: {hash_id}")
        try:
            with Session(self.engine) as session:
                stmt = select(CachedData.result).where(CachedData.hash_key == hash_id)
                result_row = session.execute(stmt).scalars().first()
            return pickle.loads(result_row) if result_row else None
        except OperationalError as e:
            self.logger.error(
                f"Failed to retrieve from cache for `{db_id}`, `{query}`, error: {e}"
            )
            return None

    def insert_in_cache(self, db_id, query: str, result: list) -> None:
        hash_id = hash_db_id_sql(db_id, query)
        self.logger.debug(
            f"Inserting (or Ignore if duplicate) in cache with hash_id: {hash_id}"
        )

        pickled_result = pickle.dumps(result)
        stmt = (
            insert(CachedData)
            .prefix_with("OR IGNORE")
            .values(hash_key=hash_id, db_id=db_id, query=query, result=pickled_result)
        )
        try:
            with Session(self.engine) as session:
                session.execute(stmt)
                session.commit()
        except OperationalError as e:
            self.logger.error(
                f"Failed to insert into cache for `{db_id}`, `{query}`, error: {e}"
            )


if __name__ == "__main__":
    cache = SQLiteCache.from_uri(db_path="test_cache.sqlite")
    uri = "test_db_uri"
    query = "SELECT * FROM yolewjwde"
    cache.insert_in_cache(
        uri, query, [("row1_col1", "row1_col2"), ("row2_col1", "row2_col2")]
    )

    cached_result = cache.get_from_cache(uri, query)
    print(cached_result)
    assert cached_result == [("row1_col1", "row1_col2"), ("row2_col1", "row2_col2")]