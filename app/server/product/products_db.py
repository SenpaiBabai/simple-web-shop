from bson import ObjectId
from fastapi import HTTPException
from pymongo import ReturnDocument

from app.server.database.db_main import collection_products
from app.server.schemas import ProductModel


class Products:
    @staticmethod
    async def add_product(product: ProductModel) -> ProductModel:
        if not product.quantity >= 1:
            raise HTTPException(status_code=400, detail="Invalid quantity of product")
        if not product.price >= 1:
            raise HTTPException(status_code=400, detail="price cannot cannot equal or be less than zero")
        check_product = await collection_products.find_one({'product_name': product.product_name})
        if check_product:
            raise HTTPException(status_code=400, detail="A product with the same name already exists")
        new_user = await collection_products.insert_one(product.model_dump(by_alias=True, exclude=["id"]))
        created_user = await collection_products.find_one({"_id": new_user.inserted_id})
        return created_user

    @staticmethod
    async def get_all_products() -> list:
        all_products = await collection_products.find().to_list(None)
        return all_products

    @staticmethod
    async def delete_product(product_id:str):
        try:
            delete_result = await collection_products.delete_one({"_id": ObjectId(product_id)})
            if delete_result.deleted_count == 1:
                return {'message': 'Product was deleted'}
            raise HTTPException(status_code=404, detail=f"Product  {product_id} not found")
        except:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")

    @staticmethod
    async def update_product(product_id:str, product):
        try:
            product = {k: v for k, v in product.model_dump(by_alias=True).items() if v is not None}
            if len(product) >= 1:
                update_result = await collection_products.find_one_and_update(
                    {"_id": ObjectId(product_id)},
                    {"$set": product},
                    return_document=ReturnDocument.AFTER,
                )
                if update_result is not None:
                    return update_result
                else:
                    raise HTTPException(status_code=400, detail=f"Incorrect product_id ")
            if (existing_product := await collection_products.find_one({"_id": product_id})) is not None:
                return existing_product
        except:
            raise HTTPException(status_code=400, detail=f"Incorrect product_id ")
