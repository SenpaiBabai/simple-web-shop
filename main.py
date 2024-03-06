from fastapi import FastAPI, Depends
from schemas import User, Product
import database as db

app = FastAPI(title="магазин на диване", )


@app.post('/registration')
async def registration(user: User = Depends()):
    response=await db.registration(user)
    return response


@app.get('/users')
async def get_all_user():
    response = await db.get_all_users()

    return response


@app.get('/products')
async def get_product():
    response = await db.get_products()
    return {'status': 200, 'products': response}


@app.get('/basket')
async def get_basket(basket_id):
    response = await db.get_basket(basket_id)
    return response


@app.post('/add_in_basket')
async def add_basket(basket_id: str, product: Product):
    response = await db.add_in_basket(basket_id, product)
    return {'status': response}


@app.get('/order')
async def get_order(order_id: str):
    response = await db.get_order(order_id)
    return response


@app.post('/order')
async def get_order(order_id):
    response = await db.add_order(order_id)
    return response
