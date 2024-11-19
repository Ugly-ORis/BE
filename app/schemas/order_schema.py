from pydantic import BaseModel, Field
from typing import List,Dict

class OrderBase(BaseModel):
    order_datetime: str = Field(..., description="주문 날짜와 시간")
    customer_id: int
    cart_id_json: List[int] = Field(..., description="판매 상품 ID 리스트")
    total_price: int = Field(..., description="총 가격")

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    order_datetime: str = Field(None, description="주문 날짜와 시간")
    cart_id_json: List[int] = Field(None, description="판매 상품 ID 리스트")
    total_price: int = None

class OrderResponse(BaseModel):
    order_id: int
    status: str = Field(..., description="주문상태, Preparing, Serving, Complete")