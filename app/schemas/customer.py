from pydantic import BaseModel, constr
from typing import Optional

class CustomerBase(BaseModel):
    name: str
    gender: str
    phone_last_digits: constr(min_length=4, max_length=4)

class CustomerCreate(CustomerBase):
    feature_vector: list[float]

class CustomerUpdate(CustomerBase):
    pass