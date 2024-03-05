from typing import List

from pydantic import BaseModel


class User(BaseModel):
    email: str
    login: str
    password: str


class Product(BaseModel):
    product_id:int
    quantity: int


class Item(BaseModel):
    item:List[Product]




