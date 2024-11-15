from pydantic import BaseModel, Field
from typing import Optional, Type, List
from fastapi import Form
import inspect

def as_form(cls: Type[BaseModel]):
    new_params = [
        inspect.Parameter(
            field_name,
            inspect.Parameter.POSITIONAL_ONLY,
            default=Form(...),
            annotation=model_field.annotation
        )
        for field_name, model_field in cls.__fields__.items()
    ]
    
    async def as_form_func(**data):
        return cls(**data)
    sig = inspect.signature(as_form_func)
    sig = sig.replace(parameters=new_params)
    as_form_func.__signature__ = sig  # type: ignore
    setattr(cls, "as_form", as_form_func)
    return cls

class IceCreamBase(BaseModel):
    name: str = Field(..., max_length=50)
    flavor: str = Field(..., max_length=200)
    price: float

@as_form
class IceCreamCreate(BaseModel):
    name: str = Field(..., max_length=50)
    flavor: str = Field(..., max_length=200)
    price: float

class IceCreamResponse(IceCreamBase):
    ice_cream_id: int

class IceCreamResponseWithImg(IceCreamBase):
    ice_cream_id: int
    image: str