from pydantic import BaseModel, Field
from typing import List

class CartBase(BaseModel):
    customer_id: int
    sale_product_id_json: List[int]

class CartCreate(CartBase):
    pass

class CartResponse(CartBase):
    cart_id: int