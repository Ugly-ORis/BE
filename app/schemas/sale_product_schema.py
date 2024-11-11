from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class SaleProductBase(BaseModel):
    ice_cream_id: int
    topping_id_json: List[int] = Field(..., description="토핑 ID 리스트")
    product_price: float

class SaleProductCreate(SaleProductBase):
    pass

class SaleProductUpdate(BaseModel):
    ice_cream_id: Optional[int] = None
    topping_id_json: Optional[List[int]] = None
    product_price: Optional[float] = None

class SaleProductResponse(SaleProductBase):
    sale_product_id: int
