from pydantic import BaseModel, Field
from typing import Optional

class ToppingBase(BaseModel):
    name: str = Field(..., max_length=20)
    extra_price: float

class ToppingCreate(ToppingBase):
    pass

class ToppingUpdate(BaseModel):
    name: Optional[str] = None
    extra_price: Optional[float] = None

class ToppingResponse(ToppingBase):
    id: int
