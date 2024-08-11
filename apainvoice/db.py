import shelve
import datetime


def get_db():
    return shelve.open("app.db", writeback=True)


def dump_db():
    import pprint

    with get_db() as db:
        pprint.pprint(dict(db))


def create_data_dict(data):
    return {"data": data, "created": datetime.datetime.now()}


class ReaderWriter:
    def write(self, key, data):
        with get_db() as db:
            db[key] = create_data_dict(data)

    def read(self, key):
        with get_db() as db:
            return db.get(key, default={})


if __name__ == "__main__":
    rw = ReaderWriter()

    # Test writing to the database
    key = "test_key"
    # data = "Hello, world!"
    # rw.write(key, data)
    # print(f"Data written with key {key}: {data}")

    # # Small delay to differentiate creation time
    # import time
    # time.sleep(1)

    # Test reading from the database
    dump_db()
