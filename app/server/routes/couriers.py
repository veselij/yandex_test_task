from fastapi import APIRouter, Body, status
from fastapi.encoders import jsonable_encoder
from server.database import add_courier
from server.models.couriers import CourierSchemaList, ResponseCourier


router = APIRouter()


@router.post('/', response_description='Added courier data to database', status_code=status.HTTP_201_CREATED)
async def add_courier_data(courier_schemas: CourierSchemaList = Body(...)):
    ids = []
    for courier_schema in courier_schemas.data:
        courier = jsonable_encoder(courier_schema)
        id = await add_courier(courier)
        ids.append({'id': id})
    return ResponseCourier(ids)
