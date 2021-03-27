from fastapi import APIRouter, Body, status, Response, HTTPException
from fastapi.encoders import jsonable_encoder
from server.database import add_obect, couriers_collection, retrieve_courier
from server.models.couriers import CouriersPostRequest, response_courier_ids, response_courier_data, CouriersIds, CourierGetResponse, CouriersValidErr, CourierItem, CourierUpdateRequest, response_courier_item
from server.assign_manager import ManagerOfOrders


router = APIRouter()


@router.post('', status_code=status.HTTP_201_CREATED, description='Import couriers', response_model=CouriersIds, response_description='Created', responses={400: {"description": "Bad request", "model": CouriersValidErr}})
async def add_courier_data(courier_schemas: CouriersPostRequest = None):
    add_fields = {'delivery_times_per_regions': {}, 'n_deliverys_per_regions': {}, 'earnings': 0, 'rating': 0}
    if courier_schemas:
        ids = await add_obect(courier_schemas.data, couriers_collection, add_fields)
        return await response_courier_ids(ids)
    else:
        raise HTTPException(status_code=400)

@router.get('/{courier_id}', status_code=status.HTTP_200_OK, description='Get courier info', response_description='OK', response_model=CourierGetResponse, responses={404: {"description": "Not found"}})
async def get_courier_data(courier_id: int):
    courier = await retrieve_courier(courier_id)
    if courier:
        return await response_courier_data(courier)
    raise HTTPException(status_code=404)

@router.patch('/{courier_id}', description='Update courier by id', status_code=status.HTTP_200_OK, response_description='Created', response_model=CourierItem, responses={400: {"description": "Bad request"}, 404: {"description": "Not found"}})
async def change_courier(courier_id: int, courier_update: CourierUpdateRequest):
    m = ManagerOfOrders(courier_id=courier_id, new_courier=jsonable_encoder(courier_update))
    if await m.deassign_ordes():
        courier = await retrieve_courier(courier_id)
        return await response_courier_item(courier)
    else:
        raise HTTPException(status_code=404)
