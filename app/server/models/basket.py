from pydantic import BaseModel, Field
from typing import List


class BasketSchema(BaseModel):
    courier_id: int = Field(..., ge=0)
    n_orders: int = 0
    n_orders_finished: int = 0
    basket_status: int = 0
    start_courier_type: str = None
    last_delivery_time: Optional[datetime] = None
    actual_weight: float = 0
    orders: List[int] = None

