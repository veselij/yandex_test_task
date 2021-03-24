from fastapi import APIRouter, Body, status, Response, HTTPException
from fastapi.encoders import jsonable_encoder
from server.database import add_obect, orders_collection
from server.models.orders import response_order_ids, OrdersIds, OrdersIdsAP, OrdersPostRequest, OrdersAssignPostRequest, OrdersCompletePostRequest, OrdersValidErr, OrdersAssignPostResponse, OrdersCompletePostResponse
from server.models.couriers import CourierSchemaForAssign
from server.assign_manager import ManagerOfOrders
from server.completion_manager import OrderComplitionManager


router = APIRouter()


@router.post('', description='Import orders', status_code=status.HTTP_201_CREATED, response_model=OrdersIds, response_description='Created', responses={400: {"description": "Bad request", "model": OrdersValidErr}})
async def add_order_data(order_schemas: OrdersPostRequest = None):
    add_fields = {'assign_time': None, 'complete_time': None, 'courier_id': None, 'basket_id': None, 'processing': 0}
    ids = await add_obect(order_schemas.data, orders_collection, add_fields)
    return response_order_ids(ids)

@router.post('/assign', status_code=status.HTTP_200_OK, description='Assign orders to a courier by id', response_description='OK', response_model=OrdersAssignPostResponse, responses={400: {"description": "Bad request"}})
async def assign_orders(courier: OrdersAssignPostRequest):
    m = ManagerOfOrders(courier_id = courier.courier_id)
    res = await m.get_result()
    if res:
        return res
    raise HTTPException(status_code=404)

@router.post('/complete', status_code=status.HTTP_200_OK, description='Marks orders as completed', response_description='OK', response_model=OrdersCompletePostResponse, responses={400: {"description": "Bad request"}} )
async def complete_order(order: OrdersCompletePostRequest):
    order = jsonable_encoder(order)
    ocm = OrderComplitionManager(order['courier_id'], order['order_id'], order['complete_time'])
    completed_order = await ocm.compleate_order()
    if completed_order:
        return {"order_id": order['order_id']}
    raise HTTPException(status_code=404)
