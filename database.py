import motor.motor_asyncio
import random
from bson.objectid import ObjectId
import config as con

number = random.randint(1, 100)

cluster = motor.motor_asyncio.AsyncIOMotorClient(
    f"mongodb+srv://{con.USER}:{con.PASSWORD}@cluster0.mc4dsnt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = cluster['DB_SHOP']
collection_users = db['users']
collection_products = db['products']
collection_backet = db['basket']
collection_orders = db['orders']


async def registration(user):
    await  collection_users.insert_one(
        {"email": user.email, 'login': user.login, 'password': user.password})
    print('пользователь успешно добавлен')


async def get_all_users():
    users = await collection_users.find().to_list(None)
    for user in users:
        user['_id'] = str(user['_id'])
    return users


async def add_product(product_id, product, price, quantity):
    await collection_products.insert_one(
        {'_id': product_id, 'product_name': product, 'price': price, 'quantity': quantity})
    print('продукт добавлен в список')


async def get_products():
    products = await collection_products.find().to_list(None)
    for product in products:
        product['_id'] = str(product['_id'])
    return products


async def reduce_product_stock(products):
    print(list(products)[0])
    for i in products:
        name_product, quantity = i[0], i[1]
        if quantity is None:
            print('nety')
        print(name_product, quantity)


async def create_basket(user_id):
    await collection_backet.insert_one({'_id': user_id, 'basket': []})
    print('корзина успешно создалась')


async def checkCondition(basket_id, product, response):
    basket = await get_basket(basket_id)

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
    for i in basket['basket']:
        total = i['quantity'] + product.quantity
        if i['product_id'] == product.product_id:
            if response['quantity'] < total:
                return True


async def add_in_basket(basket_id, product):
    obj_id = ObjectId(basket_id)
    response = await collection_products.find_one({'_id': product.product_id})
    if not response:
        return 'Товар не найдем'
    if product.quantity <= 0:
        return 'количество товара не указано или указано неверно'
    check_quantity = await check_quantity_product(basket_id, product, response)
    if check_quantity:
        return 'Недостаточно товара'
    result = await checkCondition(basket_id, product, response)
    if result:
        return 'Товар добавился в корзину'

    price = await collection_products.find_one({'_id': product.product_id})
    price = price['price']
    await collection_backet.update_one({'_id': obj_id},
                                       {'$push': {'basket': {'product_id': product.product_id, 'price': price,
                                                             'quantity': product.quantity}}})
    return 'Товар добавлен'


async def get_basket(basket_id):
    obj_id = ObjectId(basket_id)
    basket = await collection_backet.find_one({'_id': obj_id})
    basket['_id'] = str(basket['_id'])
    return basket


async def update_backet(basket_id):
    obj_id = ObjectId(basket_id)
    result = await collection_backet.update_one({'_id': obj_id}, {'$set': {'basket': []}})
    print('корзина обновлена')


async def create_orders(order_id):
    await collection_orders.insert_one({'_id': order_id, 'orders': []})
    print('заказы успешно создались')


async def add_order(order_id):
    obj_id = ObjectId(order_id)
    total_price = 0
    order = await get_basket(order_id)
    for i in order['basket']:
        total_price += i['price'] * i['quantity']
    await collection_orders.update_one({'_id': obj_id},
                                       {'$push': {'orders': {'order_id': number, 'total_price': total_price,
                                                             'order': order['basket']}}})
    await getOrderedQuantity(order_id)

    await update_backet(order_id)
    return 'заказ успешно создан'


async def get_order(orders_id):
    obj_id = ObjectId(orders_id)
    orders = await collection_orders.find_one(obj_id)
    orders['_id'] = str(orders['_id'])
    return orders


async def getOrderedQuantity(order_id):
    order = await get_basket(order_id)
    for i in order['basket']:
        product_id = i['product_id']
        quantity = i['quantity']
        result = await collection_products.update_one({'_id': product_id}, {'$inc': {'quantity': -quantity}})
        print(result)
    print('товары вычтены')


async def create_user(user):
    await registration(user)
    user_id = await collection_users.find_one({'login': user.login})
    user_id = user_id['_id']
    await create_basket(user_id)
    await create_orders(user_id)
