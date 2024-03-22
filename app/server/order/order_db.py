import asyncio
import hashlib
import json
import time

import pika
from bson import ObjectId
from fastapi import HTTPException
import config as con
from app.server.basket.basket_db import Basket
from app.server.database.db_main import collection_orders, collection_products
from app.server.schemas import OrdersModel

connection_params = pika.ConnectionParameters(host=con.host)


class OrderRep:
    @staticmethod
    async def create_order(external_id: str):

        total_price = 0
        products = []
        basket = await Basket.get_basket(external_id)
        if len(basket['basket']) == 0:
            raise HTTPException(status_code=400, detail="Basket is empty")
        for i in basket['basket']:
            total_price += i['price'] * i['quantity']
            products.append(i)
        order = OrdersModel(external_id=external_id, total_price=total_price, products=products)
        new_order = await collection_orders.insert_one(order.model_dump())
        created_user = await collection_orders.find_one({"_id": new_order.inserted_id})
        await OrderRep.getOrderedQuantity(external_id)
        await Basket.delete_basket(external_id)
        return created_user

    @staticmethod
    async def get_orders(external_id: str):
        orders = await collection_orders.find({'external_id': external_id}).to_list(None)
        if orders == []:
            raise HTTPException(status_code=404, detail="There are no orders for this external_id")
        return orders

    @staticmethod
    async def getOrderedQuantity(external_id: str):
        basket = await Basket.get_basket(external_id)
        for i in basket['basket']:
            product_id = i['_id']
            quantity = i['quantity']
            await collection_products.update_one({'_id': ObjectId(product_id)}, {'$inc': {'quantity': -quantity}})

    @staticmethod
    async def delete_order(order_id: str):
        try:
            removed_order = await collection_orders.find_one({"_id": ObjectId(order_id)})
            delete_result = await collection_orders.delete_one({"_id": ObjectId(order_id)})
            if delete_result.deleted_count == 1:
                await OrderRep.return_quantity_product(removed_order)
                return {'message': 'Order was deleted'}
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
        except:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

    @staticmethod
    async def return_quantity_product(removed_order: dict):
        try:
            for i in removed_order['products']:
                await collection_products.find_one_and_update({'_id': ObjectId(i['id'])},
                                                              {'$inc': {'quantity': i['quantity']}})
        except:
            raise HTTPException(status_code=400, detail=f"Incorect data")


class RabitMQ:
    @staticmethod
    async def get_orders(external_id: str):
        order_map = await OrderRep.get_orders(external_id)
        for order in order_map:
            order['_id'] = str(order['_id'])

        json_data = json.dumps(order_map)
        RabitMQ.send_to_queue(json_data)


    @staticmethod
    def send_to_queue(orders):
        with pika.BlockingConnection(connection_params) as connection:
            with connection.channel() as channel:
                channel.queue_declare(queue=con.unprocessed_queue)
                channel.basic_publish(exchange='', routing_key=con.unprocessed_queue, body=f'{orders}')


    @staticmethod
    def consume():
        with pika.BlockingConnection(connection_params) as connection:
            with connection.channel() as channel:
                channel.queue_declare(queue=con.processed_queue)
                while True:
                    method_frame, header_frame, body = channel.basic_get(queue=con.processed_queue, auto_ack=True)
                    if body:
                        body = body.decode('utf-8')
                        json_data = json.loads(body)
                        return json_data
