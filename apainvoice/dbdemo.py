from apainvoice import db
import sqlmodel
import typing
from pydantic import BaseModel


def get_engine():
    return db.create_engine("sqlite:///sandbox.db")


class Child(sqlmodel.SQLModel, table=True):
    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    name: str = sqlmodel.Field(index=True)
    parent: "Parent" = sqlmodel.Relationship(back_populates="children")
    parent_id: typing.Optional[int] = sqlmodel.Field(
        default=None, foreign_key="parent.id"
    )


class Parent(sqlmodel.SQLModel, table=True):
    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    name: str = sqlmodel.Field(index=True)
    children: list[Child] = sqlmodel.Relationship(back_populates="parent")


def create_stuff():
    c1 = Child(name="c1")
    c2 = Child(name="c2")
    p = Parent(name="p", children=[c1, c2])
    print(p)

    engine = get_engine()
    with sqlmodel.Session(engine) as session:
        session.add(p)
        session.commit()


if __name__ == "__main__":
    # create_stuff()

    engine = get_engine()
    with sqlmodel.Session(engine) as session:
        p = session.exec(sqlmodel.select(Parent).where(Parent.name == "p")).one()
        print(p.children[1])
