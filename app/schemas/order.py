from pydantic import BaseModel, Field
from typing import List

class OrderBase(BaseModel):
    order_datetime: str = Field(..., description="주문 날짜와 시간")
    customer_id: int
    sale_product_id_json: List[int] = Field(..., description="판매 상품 ID 리스트")
    total_price: float

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    order_datetime: str = Field(None, description="주문 날짜와 시간")
    sale_product_id_json: List[int] = Field(None, description="판매 상품 ID 리스트")
    total_price: float = None

class OrderResponse(OrderBase):
    order_id: int
