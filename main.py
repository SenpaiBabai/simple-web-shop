

from fastapi import FastAPI, Depends
from schemas import User, Product
import database as db

app = FastAPI(title="магазин на диване", )


@app.post('/registration')
async def registration(user: User = Depends()):
    await db.create_user(user)
    return {'status': 200,'message':'пользователь зарегистрировался'}


@app.get('/users')
async def get_all_user():
    response = await db.get_all_users()

    return {'status': 200, 'users': response}


@app.get('/products')
async def get_product():
    response = await db.get_products()
    return {'status': 200, 'products': response}


@app.get('/basket')
async def get_basket(basket_id):
    response = await db.get_basket(basket_id)
    return {'status': 200, 'basket': response}


@app.post('/add_in_basket')
async def add_basket(basket_id: str, product: Product):
    response = await db.add_in_basket(basket_id, product)
    return {'status': response}


@app.get('/order')
async def get_order(order_id: str):
    result = await db.get_order(order_id)
    return {'status': 200, 'orders': result}


@app.post('/order')
async def get_order(order_id):
    result = await db.add_order(order_id)
    return {'status': result}
