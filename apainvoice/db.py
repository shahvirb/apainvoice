import sqlmodel
import os
import logging

logger = logging.getLogger(__name__)


def get_db_path() -> str:
    path = os.getenv("DBPATH", "apainvoice.db")
    return f"sqlite:///{path}"


def create_engine(dbname: str = ""):
    if not dbname:
        dbname = get_db_path()
    engine = sqlmodel.create_engine(dbname)
    sqlmodel.SQLModel.metadata.create_all(engine)
    return engine


if __name__ == "__main__":
    pass
