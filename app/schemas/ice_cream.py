from pydantic import BaseModel, constr
from typing import Optional

class IceCreamBase(BaseModel):
    name: str
    flavor: str
    price: float
    stock: int

class IceCreamCreate(IceCreamBase):
    pass

class IceCreamUpdate(IceCreamBase):
    name: Optional[str] = None
    flavor: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
