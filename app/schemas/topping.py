from pydantic import BaseModel
from typing import Optional

class ToppingBase(BaseModel):
    name: str
    price: float
    availability: bool

class ToppingCreate(ToppingBase):
    pass

class ToppingUpdate(ToppingBase):
    name: Optional[str] = None
    price: Optional[float] = None
    availability: Optional[bool] = None
