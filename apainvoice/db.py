import sqlmodel


def create_engine(dbname: str = "sqlite:///apainvoice.db"):
    engine = sqlmodel.create_engine(dbname)
    sqlmodel.SQLModel.metadata.create_all(engine)
    return engine


if __name__ == "__main__":
    engine = create_engine()
    with sqlmodel.Session(engine) as session:
        pass
