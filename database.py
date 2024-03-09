import motor.motor_asyncio
import random
from bson.objectid import ObjectId
from fastapi import HTTPException

import config as con
from loguru import logger
import re

number = random.randint(1, 100)

cluster = motor.motor_asyncio.AsyncIOMotorClient(
    f"mongodb+srv://{con.USER}:{con.PASSWORD}@cluster0.mc4dsnt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = cluster['DB_SHOP']
collection_users = db['users']
collection_products = db['products']
collection_backet = db['basket']
collection_orders = db['orders']


async def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


async def registration(user):
    users = await get_all_users()
    response = await is_valid_email(user.email)
    if not response:
        raise HTTPException(status_code=404, detail="incorrect data")
    users = users['users']
    for i in users:
        if user.login == i['login'] or user.email == i['email']:
            raise HTTPException(status_code=404, detail="пользователь с такой почтой или логином уже существует")

    await  collection_users.insert_one(
        {"email": user.email, 'login': user.login, 'password': user.password})
    logger.debug('Пользователь успешно зарегистрирован')
    user_id = await collection_users.find_one({'login': user.login})
    user_id = user_id['_id']
    await create_basket(user_id)
    await create_orders(user_id)

    return {'detail': 'пользователь успешно зарегистрирован'}


async def get_all_users():
    try:
        users = await collection_users.find().to_list(None)
        for user in users:
            user['_id'] = str(user['_id'])
        return {'users': users}
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def add_product(product_id, product, price, quantity):
    await collection_products.insert_one(
        {'_id': product_id, 'product_name': product, 'price': price, 'quantity': quantity})
    logger.debug('продукт добавлен в список')


async def get_products():
    products = await collection_products.find().to_list(None)
    for product in products:
        product['_id'] = str(product['_id'])
    return products


# async def reduce_product_stock(products):
#     print(list(products)[0])
#     for i in products:
#         name_product, quantity = i[0], i[1]
#         if quantity is None:
#             print('nety')
#         print(name_product, quantity)


async def create_basket(user_id):
    await collection_backet.insert_one({'_id': user_id, 'basket': []})


async def checkCondition(basket_id, product, response):
    basket = await get_basket(basket_id)
    basket = basket['basket']
    obj_id = ObjectId(basket_id)
    count = -1

    for i in basket['basket']:
        count += 1
        if i['product_id'] == product.product_id:
            await collection_backet.update_one({'_id': obj_id},
                                               {'$inc': {f'basket.{str(count)}.quantity': product.quantity}})
            return True

    return False


async def check_quantity_product(basket_id, product, response):
    basket = await get_basket(basket_id)
    basket = basket['basket']
    for i in basket['basket']:
        total = i['quantity'] + product.quantity
        if i['product_id'] == product.product_id:
            if response['quantity'] < total:
                return True
    if response['quantity'] < product.quantity:
        return True


async def add_in_basket(basket_id, product):
    # try:
        await get_basket(basket_id)
        if type(product.product_id) != int or product.product_id is None:
            raise HTTPException(status_code=404, detail="Basket not found")
        obj_id = ObjectId(basket_id)
        response = await collection_products.find_one({'_id': product.product_id})
        if not response:
            raise HTTPException(status_code=404, detail="incorrect data")
        if product.quantity <= 0 or type(product.quantity) != int:
            raise HTTPException(status_code=400, detail="количество товара указанно некорректно")
        check_quantity = await check_quantity_product(basket_id, product, response)
        if check_quantity:
            raise HTTPException(status_code=409, detail="Недостаточно товара")
        result = await checkCondition(basket_id, product, response)
        if result:
            return {'message': 'Товар добавился в корзину'}

        price = await collection_products.find_one({'_id': product.product_id})
        price = price['price']
        await collection_backet.update_one({'_id': obj_id},
                                           {'$push': {'basket': {'product_id': product.product_id, 'price': price,
                                                                 'quantity': product.quantity}}})
        return {'message': 'Товар добавлен'}
    # except:
    #     raise HTTPException(status_code=404, detail="incorrect data")


async def get_basket(basket_id):
    try:
        obj_id = ObjectId(basket_id)
        basket = await collection_backet.find_one({'_id': obj_id})

        basket['_id'] = str(basket['_id'])
        return {'basket': basket}
    except:
        raise HTTPException(status_code=404, detail="Basket not found")


async def update_backet(basket_id):
    obj_id = ObjectId(basket_id)
    result = await collection_backet.update_one({'_id': obj_id}, {'$set': {'basket': []}})
    logger.debug('корзина обновлена')


async def create_orders(order_id):
    await collection_orders.insert_one({'_id': order_id, 'orders': []})
    logger.debug('заказы успешно создались')


async def add_order(order_id):
    total_price = 0
    basket = await get_basket(order_id)
    basket = basket['basket']
    if len(basket['basket']) == 0:
        raise HTTPException(status_code=404, detail="корзина пуста")
    obj_id = ObjectId(order_id)

    for i in basket['basket']:
        total_price += i['price'] * i['quantity']
    await collection_orders.update_one({'_id': obj_id},
                                       {'$push': {'orders': {'order_id': number, 'total_price': total_price,
                                                             'order': basket['basket']}}})
    await getOrderedQuantity(order_id)

    await update_backet(order_id)
    return {'message': 'заказ успешно создан'}


async def get_order(orders_id):
    try:
        obj_id = ObjectId(orders_id)
        orders = await collection_orders.find_one(obj_id)
        orders['_id'] = str(orders['_id'])
        return {'orders': orders}
    except:
        raise HTTPException(status_code=404, detail="заказ с таким id  не был найден")


async def getOrderedQuantity(order_id):
    order = await get_basket(order_id)
    order = order['basket']
    for i in order['basket']:
        product_id = i['product_id']
        quantity = i['quantity']
        await collection_products.update_one({'_id': product_id}, {'$inc': {'quantity': -quantity}})
    logger.debug('товары вычтены')
