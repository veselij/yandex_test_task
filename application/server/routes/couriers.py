from fastapi import APIRouter, Body, status
from fastapi.encoders import jsonable_encoder
from server.database import add_obect, couriers_collection, retrieve_courier
from server.models.couriers import CourierSchemaList, response_courier_ids, response_courier_data


router = APIRouter()


@router.post('', response_description='Added courier data to database', status_code=status.HTTP_201_CREATED)
async def add_courier_data(courier_schemas: CourierSchemaList = Body(...)):
    ids = await add_obect(courier_schemas.data, couriers_collection)
    return response_courier_ids(ids)

@router.get('/{courier_id}', response_description='Get courier data')
async def get_courier_data(courier_id):
    courier = await retrieve_courier(int(courier_id))
    return response_courier_data(courier)
