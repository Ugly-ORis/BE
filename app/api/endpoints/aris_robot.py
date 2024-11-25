from fastapi import FastAPI, APIRouter, Depends, WebSocket
from app.schemas.aris_robot_schema import RobotCreate, RobotUpdate
from app.services.aris_robot_service import RobotService
from app.api.dependencies import robot_client
import numpy as np
import cv2
import asyncio
from PIL import Image


def get_robot_service() -> RobotService:
    return RobotService(robot_client)

router = APIRouter()

@router.post("/robot", summary="로봇 동작")
async def start_robot(robot_service: RobotService = Depends(get_robot_service)):
    """
    로봇 동작 기능
    """
    robot_service.run() 


# @router.post("/robot", summary="로봇 동작")
# async def start_robot():
#     """
#     로봇 동작 기능
#     """
#     RobotService.run()
    
    # await RobotService.robot_action()
    # await RobotService.emergency()