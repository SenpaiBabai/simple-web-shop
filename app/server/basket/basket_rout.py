from typing import List

from fastapi import APIRouter, Body
from starlette import status

from app.server.basket.basket_db import Basket
from app.server.schemas import BasketCollections, ProductModel, ProductAdd, ProductAddCollections

router = APIRouter(
    prefix="/basket",
    tags=["basket"],

)


@router.get(
    "/{external_id}",
    description='Endpoint which shows the users basket',
    response_description="User basket",
    response_model=BasketCollections,
    response_model_by_alias=False,
)
async def get_basket(external_id: str):
    basket = await Basket.get_basket(external_id)
    return basket


@router.post(
    "/add_in_basket",
    description='Endpoint that adds product in basket',
    response_description="User basket",
    response_model=BasketCollections,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def add_in_basket(external_id: str, product: List[ProductAdd] = Body()):
    result = await Basket.add_in_basket(external_id, product)
    print(result)
    return result


@router.delete('/delete_basket',
               description='Endpoint that cleans the basket')
async def delete_basket(external_id: str):
    result = await Basket.delete_basket(external_id)
    return result


@router.delete('/delete_basket/{product_id}}', description='Endpoint which removes a product from the basket')
async def delete_product_basket(product_id: str, external_id: str):
    delete_product_result = await Basket.delete_product_fr_basket(external_id, product_id)
    return delete_product_result
