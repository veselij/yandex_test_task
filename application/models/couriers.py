from typing import Optional, List
from pydantic import BaseModel, Field
from constant import COURIER_TYPE
from pydantic import Extra
from enum import Enum


class CourierType(str, Enum):
    foot = 'foot'
    bike = 'bike'
    car = 'car'


class Courier(BaseModel, extra=Extra.forbid):
    id: int = Field(..., ge=0)


class CouriersIds(BaseModel, extra=Extra.forbid):
    couriers: List[Courier]


class CouriersValidErr(BaseModel, extra=Extra.forbid):
    validation_error: CouriersIds = Field(...)


class CourierItem(BaseModel):
    courier_id: int = Field(..., ge=0)
    courier_type: CourierType = Field(...)
    regions: List[int] = Field(..., ge=0)
    working_hours: List[str] = Field(...)

    class Config:
        schema_extra= {
                'example': {
                    'courier_id': 1,
                    'courier_type': 'foot',
                    'regions': [1, 2, 4],
                    'working_hours': ['11:35-14:05', '09:00-11:00']
                    }
                }
        extra = Extra.forbid


class CouriersPostRequest(BaseModel, extra=Extra.forbid):
    data: List[CourierItem] = Field(...)


class CourierGetResponse(BaseModel, extra=Extra.allow):
    courier_id: int = Field(..., ge=0)
    courier_type: CourierType = Field(...)
    regions: List[int] = Field(..., ge=0)
    working_hours: List[str] = Field(...)
    earnings: float = Field(...)


class CourierUpdateRequest(BaseModel, extra=Extra.forbid):
    courier_type: Optional[CourierType]
    regions: Optional[List[int]]
    working_hours: Optional[List[str]]


class CourierSchemaForAssign(BaseModel, extra=Extra.forbid):
    courier_id: int = Field(..., ge=0)


async def response_courier_ids(data):
    ids = []
    for d in data:
        ids.append({'id': d['courier_id']})
    return {'couriers': ids}


async def response_courier_data(data):
    response = dict(data)
    response.pop('_id')
    response.pop('delivery_times_per_regions')
    if not data['n_deliverys_per_regions']:
        response.pop('rating')
    response.pop('n_deliverys_per_regions')
    return response

async def response_courier_item(data):
    response = dict(data)
    response.pop('_id')
    response.pop('delivery_times_per_regions')
    response.pop('n_deliverys_per_regions')
    response.pop('earnings')
    response.pop('rating')
    return response

