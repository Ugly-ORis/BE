from pydantic import BaseModel, Field
from typing import List

class SaleProductBase(BaseModel):
    ice_cream_id: int
    topping_id_json: List[int] 
    product_price: float

class SaleProductCreate(SaleProductBase):
    pass

class SaleProductResponse(SaleProductBase):
    sale_product_id: int