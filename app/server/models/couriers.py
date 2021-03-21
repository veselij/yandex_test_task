from typing import Optional, List, Dict
from pydantic import BaseModel, Field, validator
from server.constant import COURIER_TYPE
from pydantic import Extra

class CourierSchema(BaseModel):
    courier_id: int = Field(..., ge=0)
    courier_type: str = Field(...)
    regions: List[int] = Field(...)
    working_hours: List[str] = Field(...)
    rating: Optional[float] = 0
    earnings: Optional[float] = 0
    delivery_times_per_regions: Optional[Dict] = {}
    n_deliverys_per_regions: Optional[Dict] = {}

    @validator('courier_type')
    def courier_type_check(cls, v):
        if v not in COURIER_TYPE:
            raise ValueError('only following courier_id supported {}'.format(', '.join(COURIER_TYPE)))
        return v
    @validator('regions', each_item=True)
    def regions_positive_value_check(cls, v):
        if v < 0:
            raise ValueError('only positive values in regions')
        return v

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

class CourierSchemaList(BaseModel):
    data: Optional[List[CourierSchema]] = None



def ResponseCourier(data):
    ids = []
    for d in data:
        ids.append({'id': d['courier_id']})
    return {'couriers': ids}

class CourierSchemaForAssign(BaseModel):
    courier_id: int = Field(..., ge=0)

