from pydantic import BaseModel
from typing import Optional

class SaleProductBase(BaseModel):
    product_name: str
    description: Optional[str] = None
    price: float

class SaleProductCreate(SaleProductBase):
    pass

class SaleProductUpdate(SaleProductBase):
    product_name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
