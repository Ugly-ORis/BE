from pydantic import BaseModel, constr
from typing import Optional

class TopcamBase(BaseModel):
    marker_id:int
    location:str

class TopcamCreate(TopcamBase):
    id : int
    pass
