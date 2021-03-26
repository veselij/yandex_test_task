from typing import Optional, List
from pydantic import BaseModel, Field, validator
from pydantic import Extra
from datetime import datetime


class Order(BaseModel, extra=Extra.forbid):
    id: int = Field(..., ge=0)


class OrdersIds(BaseModel, extra=Extra.forbid):
    orders: List[Order]


class OrdersValidErr(BaseModel, extra=Extra.forbid):
    validation_error: OrdersIds = Field(...)


class OrderItem(BaseModel):
    order_id: int = Field(..., ge=0)
    weight: float = Field(..., ge=0.01, le=50.00)
    region: int = Field(..., ge=0)
    delivery_hours: List[str] = Field(...)

    class Config:
        schema_extra = {
                'example': {
                    "order_id": 1,
                    "weight": 0.23,
                    "region": 12,
                    "delivery_hours": ["09:00-18:00"]
                    }
                }
        extra = Extra.forbid


class OrdersPostRequest(BaseModel, extra=Extra.forbid):
    data: Optional[List[OrderItem]] = Field(...)


def response_order_ids(data):
    ids = []
    for d in data:
        ids.append({'id': d['order_id']})
    return {'orders': ids}


class OrdersCompletePostRequest(BaseModel, extra=Extra.forbid):
    courier_id: int = Field(...)
    order_id: int = Field(...)
    complete_time: str = Field(...)


class OrdersCompletePostResponse(BaseModel, extra=Extra.forbid):
    order_id:int = Field(...)


class OrdersAssignPostRequest(BaseModel, extra=Extra.forbid):
    courier_id: int = Field(...)


class OrdersAssignPostResponse(BaseModel, extra=Extra.forbid):
    orders: List[Order]
    assign_time: Optional[str]

