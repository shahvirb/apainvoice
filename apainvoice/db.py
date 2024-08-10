import shelve


def get_db():
    return shelve.open("app.db", writeback=True)
