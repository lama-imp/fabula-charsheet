from pydantic import BaseModel


class Item(BaseModel):
    name: str = ""
    cost: int = 0
    quality: str = "No Quality"
