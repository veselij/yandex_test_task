from typing import Optional, List, Dict
from pydantic import BaseModel, Field, validator
from server.constant import COURIER_TYPE
from pydantic import Extra
from enum import Enum


class CourierType(str, Enum):
    foot = 'foot'
    bike = 'bike'
    car = 'car'


class Courier(BaseModel):
    id: int = Field(...)

    class Config:
        extra = Extra.forbid


class CouriersIds(BaseModel):
    couriers: List[Courier]

    class Config:
        extra = Extra.forbid


class CouriersIdsAP(BaseModel):
    couriers: List[Courier]


class CouriersValidErr(BaseModel):
    validation_error: CouriersIdsAP = Field(...)

    class Config:
        extra = Extra.forbid


class CourierItem(BaseModel):
    courier_id: int = Field(...)
    courier_type: CourierType = Field(...)
    regions: List[int] = Field(...)
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


class CouriersPostRequest(BaseModel):
    data: List[CourierItem] = Field(...)

    class Config:
        extra = Extra.forbid


class CourierGetResponse(BaseModel):
    courier_id: int = Field(...)
    courier_type: CourierType = Field(...)
    regions: List[int] = Field(...)
    working_hours: List[str] = Field(...)
    rating: Optional[float] = 0
    earnings: Optional[float] = 0

    class Config:
        extra = Extra.forbid


class CourierUpdateRequest(BaseModel):
    courier_type: Optional[CourierType]
    regions: Optional[List[int]]
    working_hours: Optional[List[str]]

    class Config:
        extra = Extra.forbid


class CourierSchemaForAssign(BaseModel):
    courier_id: int = Field(...)


def response_courier_ids(data):
    ids = []
    for d in data:
        ids.append({'id': d['courier_id']})
    return {'couriers': ids}


def response_courier_data(data):
    response = dict(data)
    response.pop('_id')
    response.pop('delivery_times_per_regions')
    response.pop('n_deliverys_per_regions')
    if sum(data['n_deliverys_per_regions'].values()) == 0:
        response.pop('rating')
    return response

def response_courier_item(data):
    response = dict(data)
    response.pop('_id')
    response.pop('delivery_times_per_regions')
    response.pop('n_deliverys_per_regions')
    response.pop('earnings')
    response.pop('rating')
    return response

