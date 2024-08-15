import datetime
import shelve
import sqlmodel


# TODO remove all this
def get_shelve_db():
    return shelve.open("app.db", writeback=True)


def dump_shelve_db():
    import pprint

    with get_shelve_db() as db:
        pprint.pprint(dict(db))


def create_data_dict(data):
    return {"data": data, "created": datetime.datetime.now()}


class ReaderWriter:
    def write(self, key, data):
        with get_shelve_db() as db:
            db[key] = create_data_dict(data)

    def read(self, key):
        with get_shelve_db() as db:
            return db.get(key, default={})


# --- end TODO


def create_engine(dbname: str = "sqlite:///app.db"):
    engine = sqlmodel.create_engine(dbname)
    sqlmodel.SQLModel.metadata.create_all(engine)
    return engine


if __name__ == "__main__":
    engine = create_engine()
    with sqlmodel.Session(engine) as session:
        pass
