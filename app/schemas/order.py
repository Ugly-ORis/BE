from pydantic import BaseModel, conlist
from typing import List, Optional
from datetime import datetime

class OrderBase(BaseModel):
    customer_id: int
    sale_product_ids: List[int] 
    total_price: float

class OrderCreate(OrderBase):
    order_datetime: datetime

class OrderUpdate(OrderBase):
    customer_id: Optional[int] = None
    sale_product_ids: Optional[List[int]] = None
    total_price: Optional[float] = None
    order_datetime: Optional[datetime] = None
