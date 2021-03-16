from typing import Optional, List
from pydantic import BaseModel, Field, validator
from pydantic import Extra
from datetime import datetime


class OrderSchema(BaseModel):
    order_id: int = Field(..., ge=0)
    weight: float = Field(..., ge=0.01, le=50.00)
    region: int = Field(..., ge=0)
    delivery_hours: List[str] = Field(...)
    assign_time: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    courier_id: Optional[int] = None

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

class OrderSchemaList(BaseModel):
    data: Optional[List[OrderSchema]] = None


def ResponseOrder(data):
    return {'orders': data}

