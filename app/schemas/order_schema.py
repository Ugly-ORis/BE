from pydantic import BaseModel, Field
from typing import List

class OrderBase(BaseModel):
    order_datetime: str = Field(..., description="주문 날짜와 시간")
    customer_id: int
    cart_id: int
    total_price: int = Field(..., description="총 가격")
    status: str

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    order_id: int