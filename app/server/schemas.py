from typing import Optional, Annotated, List
from bson import ObjectId
from pydantic.functional_validators import BeforeValidator
from pydantic import BaseModel, EmailStr, Field, ConfigDict

PyObjectId = Annotated[str, BeforeValidator(str)]


class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: EmailStr = Field(...)
    login: str = Field(...)
    password: str = Field(...)
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True,
                              json_schema_extra={
                                  "example": {
                                      "email": "abisus@gmail.com",
                                      "login": "abibus",
                                      "password": "bumbampup"

                                  }
                              }
                              )


class UserCollections(BaseModel):
    users: List[UserModel]


class ProductAdd(BaseModel):
    id: str
    quantity: int


class ProductAddCollections(BaseModel):
    products: List[ProductAdd]


class ProductModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    product_name: str = Field(...)
    price: float = Field(...)
    quantity: int = Field(...)
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True,
                              json_schema_extra={
                                  'example': {
                                      'product_name': 'string',
                                      'price': 0,
                                      'quantity': 0,

                                  }})


class ProductCollections(BaseModel):
    products: List[ProductModel]


class UpdateProductModel(BaseModel):
    product_name: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "name": "string",
                "price": 0,
                "quantity": 0,
            }
        },
    )


class BasketModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    external_id: Optional[PyObjectId] = Field(default=None)
    basket: list = Field(default=[])


class BasketCollections(BasketModel):
    basket: List[ProductModel]


class OrdersModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    external_id: Optional[PyObjectId] = Field(default=None)
    total_price: Optional[float] = None
    products: List[ProductModel]


class OrderCollections(BaseModel):
    orders: List[OrdersModel]


class Product_in_order(BaseModel):
    product_name: str
    price: float
    quantity: int

class Order(BaseModel):
    user_id: str
    total_price: float
    products: List[Product_in_order]
