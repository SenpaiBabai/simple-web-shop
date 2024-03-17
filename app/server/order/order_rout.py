from fastapi import APIRouter

from app.server.order.order_db import OrderRep
from app.server.schemas import OrdersModel, OrderCollections

router = APIRouter(
    prefix="/orders",
    tags=["orders"], )


@router.get('/', response_model=OrderCollections,
            description='Endpoint which shows all user orders',
            response_description='list orders')
async def get_order(external_id):
    # orders = await OrderRep.get_orders(external_id)
    return OrderCollections(orders=await OrderRep.get_orders(external_id))


@router.post("/", response_model=OrdersModel,
             description='Endpoint which creates the order',
             response_description='Order')
async def add_order(external_id):
    order = await OrderRep.create_order(external_id)
    return order


@router.delete("/{order_id}",description='Endpoint which removes order')
async def delete_order(order_id: str):
    delete_result = await OrderRep.delete_order(order_id)
    return delete_result
