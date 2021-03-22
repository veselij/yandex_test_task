from fastapi import APIRouter, Body, status, Response
from fastapi.encoders import jsonable_encoder
from server.database import add_obect, orders_collection
from server.models.orders import OrderSchemaList, ResponseOrder, OrderSchemaForComplete
from server.models.couriers import CourierSchemaForAssign
from server.assign_manager import ManagerOfOrders
from server.completion_manager import OrderComplitionManager


router = APIRouter()


@router.post('', response_description='Added order data to database', status_code=status.HTTP_201_CREATED)
async def add_order_data(order_schemas: OrderSchemaList = Body(...)):
    ids = await add_obect(order_schemas.data, orders_collection)
    return ResponseOrder(ids)

@router.post('/assign', response_description='Assign orders for courier', status_code=status.HTTP_200_OK)
async def assign_orders(courier: CourierSchemaForAssign, response: Response):
    m = ManagerOfOrders(courier_id = courier.courier_id)
    res = await m.get_result()
    if res:
        return res
    response.status_code = status.HTTP_400_BAD_REQUEST
    return

@router.post('/complete', response_description='Complete order', status_code=status.HTTP_400_BAD_REQUEST)
async def complete_order(order: OrderSchemaForComplete, response: Response):
    order = jsonable_encoder(order)
    ocm = OrderComplitionManager(order['courier_id'], order['order_id'], order['complete_time'])
    completed_order = await ocm.compleate_order()
    if completed_order:
        response.status_code=status.HTTP_200_OK
        return {"order_id": order['order_id']}
    return
