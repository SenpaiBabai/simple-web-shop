from bson import ObjectId
from fastapi import HTTPException
from starlette import status

from app.server.basket.basket_db import Basket
from app.server.database.db_main import collection_users
from app.server.order.order_db import OrderRep
from app.server.schemas import UserModel
from fastapi.responses import Response


class User:
    @staticmethod
    async def create_user(user: UserModel) -> UserModel:
        print(user.model_dump())
        check_email = await collection_users.find_one({"email": user.email})
        if check_email:
            raise HTTPException(status_code=400, detail="A user with this email already registered")
        check_login = await collection_users.find_one({'login': user.login})
        if check_login:
            raise HTTPException(status_code=400, detail="A user with this login is already registered")
        new_user = await collection_users.insert_one(user.model_dump(by_alias=True, exclude=["id"]))
        created_user = await collection_users.find_one({"_id": new_user.inserted_id})
        await Basket.create_basket(new_user.inserted_id)
        # await OrderRep.create_order(new_user.inserted_id)
        return created_user

    @staticmethod
    async def get_all_users()->list:
        all_users = await collection_users.find().to_list(None)
        print(all_users)
        return all_users

    @staticmethod
    async def delete_user(user_id:str):
        try:
            delete_result = await collection_users.delete_one({"_id": ObjectId(user_id)})
            if delete_result.deleted_count == 1:
                return {'message':'User was deleted'}
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        except:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
