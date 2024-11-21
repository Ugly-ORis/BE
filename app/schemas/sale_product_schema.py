from app.schemas.topping_schema import ToppingBase
from pydantic import BaseModel, Field
from typing import List

class SaleProductBase(BaseModel):
    ice_cream_id: int
    topping_id_json: List[int] 
    product_price: float

class SaleProductCreate(SaleProductBase):
    pass

class SaleProductListResponse(SaleProductBase):
    sale_product_id: int
    
class SaleProductResponse(SaleProductBase):
    sale_product_id: int
    ice_cream_name: str
    topping_data: List[ToppingBase]