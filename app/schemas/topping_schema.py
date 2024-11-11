from pydantic import BaseModel, Field
from typing import Optional

class ToppingBase(BaseModel):
    name: str = Field(..., max_length=20)
    extra_price: float

class ToppingCreate(ToppingBase):
    pass

class ToppingResponse(ToppingBase):
    topping_id: int