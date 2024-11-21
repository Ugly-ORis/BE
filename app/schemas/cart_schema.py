from app.schemas.sale_product_schema import SaleProductResponse
from pydantic import BaseModel, Field
from typing import List

class CartBase(BaseModel):
    customer_id: int
    sale_product_id_json: List[int]

class CartCreate(CartBase):
    pass

class CartListResponse(CartBase):
    cart_id: int
    
class CartResponse(CartBase):
    cart_id: int
    sale_products: List[SaleProductResponse] 