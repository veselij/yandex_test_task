from fastapi import APIRouter, Body, status, Response
from fastapi.encoders import jsonable_encoder
from server.database import add_order, retrieve_courier, retrieve_orders, update_order
from server.models.orders import OrderSchemaList, ResponseOrder
from server.models.couriers import CourierSchemaForAssign
from server.constant import COURIER_MAX_WEIGHT


router = APIRouter()


@router.post('/', response_description='Added order data to database', status_code=status.HTTP_201_CREATED)
async def add_order_data(order_schemas: OrderSchemaList = Body(...)):
    ids = []
    for order_schema in order_schemas.data:
        order = jsonable_encoder(order_schema)
        id = await add_order(order)
        ids.append({'id': id})
    return ResponseOrder(ids)

@router.post('/assign', response_description='Assign orders for courier', status_code=status.HTTP_200_OK)
async def assign_orders(courier: CourierSchemaForAssign, response: Response):
    courier_id = courier.courier_id
    courier_obj = await retrieve_courier(courier_id)
    if not courier_obj:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return
    max_weight = COURIER_MAX_WEIGHT[courier_obj['courier_type']]
    regions = courier_obj['regions']
    orders_ids = []
    async for order in await retrieve_orders(max_weight, regions):
        orders_ids.append(order['order_id'])
    if orders_ids:
        assign_time = await update_order(orders_ids, courier_id)
        resp_ids = [{'id':i} for i in orders_ids]
        return {"orders": resp_ids, "assign_time":  assign_time}
    return {"orders": []}
