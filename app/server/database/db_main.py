import motor.motor_asyncio
import config as con
cluster = motor.motor_asyncio.AsyncIOMotorClient(
    f"mongodb+srv://{con.USER}:{con.PASSWORD}@cluster0.mc4dsnt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = cluster['DB_SHOP']
collection_users = db['users']
collection_products = db['products']
collection_backet = db['basket']
collection_orders = db['orders']

