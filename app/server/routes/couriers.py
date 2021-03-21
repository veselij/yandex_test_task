from fastapi import APIRouter, Body, status
from fastapi.encoders import jsonable_encoder
from server.database import add_obect, couriers_collection
from server.models.couriers import CourierSchemaList, ResponseCourier


router = APIRouter()


@router.post('/', response_description='Added courier data to database', status_code=status.HTTP_201_CREATED)
async def add_courier_data(courier_schemas: CourierSchemaList = Body(...)):
    ids = await add_obect(courier_schemas.data, couriers_collection)
    return ResponseCourier(ids)
