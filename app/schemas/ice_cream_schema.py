from pydantic import BaseModel, Field
from typing import Optional

class IceCreamBase(BaseModel):
    name: str = Field(..., max_length=50)
    flavor: str = Field(..., max_length=200)
    price: float

class IceCreamCreate(IceCreamBase):
    pass

class IceCreamUpdate(BaseModel):
    name: Optional[str] = None
    flavor: Optional[str] = None
    price: Optional[float] = None

class IceCreamResponse(IceCreamBase):
    ice_cream_id: int
