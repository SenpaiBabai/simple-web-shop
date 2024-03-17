import asyncio
from typing import List

from bson import ObjectId
from fastapi import HTTPException
from pymongo import ReturnDocument

from app.server.database.db_main import collection_backet, collection_products
from app.server.schemas import ProductAdd, BasketModel, ProductAddCollections


class Basket:
    @staticmethod
    async def create_basket(external_id:str):
        basket = BasketModel(external_id=external_id)
        await collection_backet.insert_one(basket.model_dump(by_alias=True, exclude=["id"]))

    @staticmethod
    async def get_basket(external_id:str):
        try:
            basket = await collection_backet.find_one({'external_id': external_id})
            if not basket:
                raise HTTPException(status_code=400, detail=f"Incorect data")
            return basket
        except:
            raise HTTPException(status_code=400, detail=f"Incorect data")

    @staticmethod
    async def add_in_basket(external_id: str, product_res: List[ProductAdd]):
        for product in product_res:
            if product.quantity <= 0:
                raise HTTPException(status_code=400, detail=f"quantity cannot be less than or equal to zero")
            check_quantity = await Basket.check_quantity_product(external_id, product)
            if check_quantity:
                raise HTTPException(status_code=400, detail=f"not enough {product.id}")

            products = await collection_products.find_one({'_id': ObjectId(product.id)})
            products['quantity'] = product.quantity
            check_product_in_basket = await Basket.checkCondition(external_id, product)
            if check_product_in_basket:
                continue

            await collection_backet.find_one_and_update({'external_id': external_id},
                                                        {'$push': {'basket': products}})

        basket = await Basket.get_basket(external_id)

        return basket

    @staticmethod
    async def checkCondition(external_id: str, product_res: ProductAdd):
        basket = await Basket.get_basket(external_id)
        basket = basket['basket']
        count = -1
        if len(basket) == 0:
            return False
        for i in basket:
            count += 1
            if i['_id'] == ObjectId(product_res.id):
                await collection_backet.find_one_and_update({'external_id': external_id},
                                                            {'$inc': {
                                                                f'basket.{str(count)}.quantity': product_res.quantity}})

                return True

        return False

    @staticmethod
    async def check_quantity_product(external_id:str, product: ProductAdd):
        try:
            product_res = await collection_products.find_one({'_id': ObjectId(product.id)})
            basket = await Basket.get_basket(external_id)
            for i in basket['basket']:
                total = i['quantity'] + product.quantity
                if i['_id'] == ObjectId(product.id):
                    if product_res['quantity'] < total:
                        return True
                    else:
                        return False
            if product_res['quantity'] < product.quantity:
                return True
        except:
            raise HTTPException(status_code=400, detail=f"Incorect data")

    @staticmethod
    async def delete_basket(external_id:str):
        await Basket.get_basket(external_id)
        await collection_backet.update_one({'external_id': external_id}, {'$set': {'basket': []}})
        return {'message': 'the basket has been emptied'}

    @staticmethod
    async def delete_product_fr_basket(external_id:str, product_id:str):
        try:
            ObjectId(product_id)
        except:
            raise HTTPException(status_code=400, detail=f"Incorect product_id")

        check_basket= await collection_backet.find_one({'external_id':external_id})
        check_product = await collection_backet.find_one(
            {"external_id": external_id, "basket": {"$elemMatch": {"_id": ObjectId(product_id)}}}
        )
        if check_basket == None:
            raise HTTPException(status_code=404, detail=f"Basket with this id was not found")
        if check_product == None:
            raise HTTPException(status_code=404, detail=f"This product is not in the cart")

        delete_result = await collection_backet.update_one(
            {"external_id": external_id},
            {"$pull": {"basket": {"_id": ObjectId(product_id)}}}
        )

        if delete_result.modified_count == 1:
            return {'message': 'The product has been removed from the Basket'}
