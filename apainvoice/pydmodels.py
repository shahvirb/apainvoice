from pydantic import BaseModel, Field


class PlayerBill(BaseModel):
    name: str
    amount: int
