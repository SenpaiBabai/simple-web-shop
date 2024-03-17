from fastapi import APIRouter, Body, Depends
from starlette import status

from app.server.product.products_db import Products
from app.server.schemas import ProductModel, ProductCollections, UpdateProductModel

router = APIRouter(
    prefix="/products",
    tags=["products"],)



@router.get(
    "/",
    description='Endpoint that show all products',
    response_description="List all products",
    response_model=ProductCollections,
    response_model_by_alias=False,
)
async def list_products():
    return ProductCollections(products=await Products.get_all_products())


@router.post(
    "/",
    description='Endpoint that adds a new product',
    response_description="New product",
    response_model=ProductModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_product(product: ProductModel = Body()):
    new_product = await Products.add_product(product)
    return new_product


@router.put(
    "/{product_id}",
    description='Endpoint which updates product data',
    response_description="Update a product",
    response_model=ProductModel,
    response_model_by_alias=False,
)
async def update_student(product_id: str, product: UpdateProductModel = Depends()):
    result_update= await Products.update_product(product_id,product)
    return result_update


@router.delete("/{product_id}", description="Enpoint which removes the product")
async def delete_user(product_id: str):
    delete_result = await Products.delete_product(product_id)
    return delete_result

