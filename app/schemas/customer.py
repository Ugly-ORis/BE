from pydantic import BaseModel, constr
from typing import List

class CustomerBase(BaseModel):
    name: str
    phone_last_digits: constr(min_length=4, max_length=4)

class CustomerCreate(CustomerBase):
    feature_vector: List[float] 

class CustomerUpdate(CustomerBase):
    pass
