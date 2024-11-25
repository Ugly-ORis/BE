from pydantic import BaseModel, constr
from typing import Optional

class RobotBase(BaseModel):
    name: str

class RobotCreate(RobotBase):
    feature_vector: list[float]

class RobotUpdate(RobotBase):
    pass