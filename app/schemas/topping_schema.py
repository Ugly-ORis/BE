from pydantic import BaseModel, Field
from typing import Type
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
    as_form_func.__signature__ = sig
    setattr(cls, "as_form", as_form_func)
    return cls

class ToppingBase(BaseModel):
    name: str = Field(..., max_length=20)
    extra_price: float

@as_form
class ToppingCreate(ToppingBase):
    name: str = Field(..., max_length=50)
    extra_price: float

class ToppingResponse(ToppingBase):
    topping_id: int
    
class ToppingResponseWithImg(ToppingBase):
    topping_id: int
    image: str
