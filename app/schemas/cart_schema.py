from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class CartBase(BaseModel):
    ice_cream_id: int
    topping_id: int
    product_price: int

class CartCreate(CartBase):
    pass

class CartUpdate(BaseModel):
    ice_cream_id: Optional[int] = None
    topping_id: Optional[int] = None
    product_price: Optional[int] = None

class CartResponse(CartBase):
    cart_id: int
    customer_id:int

class CartNameResponse(CartBase):
    cart_id: int
    customer_id: int
    ice_cream_name: str
    topping_name: str