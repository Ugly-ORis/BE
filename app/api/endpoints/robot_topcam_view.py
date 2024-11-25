from fastapi import APIRouter, HTTPException, Depends, WebSocket
# from app.schemas.robot_topcam_view import topcamCreate, 
from app.schemas.topcam_schema import TopcamCreate
from app.services.robot_topcam_view import topcamService
from app.api.dependencies import topcam_client
from typing import List
import cv2, time, queue
# import sys
# import os

import asyncio

def get_marker_id_service() -> topcamService:
    return topcamService(topcam_client)


router = APIRouter()

@router.websocket("/top")
async def create_topcam_id(websocket: WebSocket, service: topcamService = Depends(get_marker_id_service)):
    await websocket.accept()
    service.get_topcam_id(websocket)
    await websocket.close()
    
### websocker 기능불러오기 2
# @router.websocket("/top")
# async def get_topcam_id(websocket: WebSocket, service: topcamService = Depends(get_marker_id_service)):
#     await websocket.accept()
#     await service.yolo_run(websocket)
#     await websocket.close()


##### websocket code 기능은 불러오는 방식으로
# @router.websocket("/top")
# async def get_topcam_id(websocket: WebSocket, service: topcamService = Depends(yolo_run_service)):
#     marker_id = service.get_marker_id(websocket)
#     return {"marker_id": marker_id, "message": "Detecting Aruco Marker ID"}



# ####### websocket code 기능 포함

# from BE.xArm_Python_SDK.robot_action import RobotMain
# from xarm.wrapper import XArmAPI
# from xarm import version
# import asyncio

# RobotMain.pprint('xArm-Python-SDK Version:{}'.format(version.__version__))
# arm = XArmAPI('192.168.1.184', baud_checkset=False)
# robot = RobotMain(arm)

# @router.websocket("/top")
# async def get_topcam_id(websocket: WebSocket):
#     await websocket.accept()
#     # await websocket.send_json({"message": f"Welcome back!"})
    
#     # ArUco 사전 (marker dictionary)와 marker size (예: 6x6 크기의 마커)
#     aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
#     parameters = cv2.aruco.DetectorParameters()
    
#     # 웹캠 열기
#     cap = cv2.VideoCapture(2)

#     # 특정 마커 ID 설정 (이 ID의 마커가 사라졌을 때 트리거)
#     target_marker_ids = {0,5,7}  # 사라짐을 감지할 마커 ID 집합
#     marker_lost_times = {marker_id: None for marker_id in target_marker_ids}  # 각 마커의 사라짐 시간
#     timeout_duration = 3  # 사라짐 확인 시간 (초)
#     marker_queue = queue.Queue()

#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break

#         # Grayscale 변환
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#         # ArUco 마커 감지
#         corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

#         # 현재 감지된 마커 ID 목록을 집합으로 만듦
#         detected_ids = set(ids.flatten()) if ids is not None else set()

#         # 감지된 마커 그리기
#         if ids is not None:
#             cv2.aruco.drawDetectedMarkers(frame, corners, ids)

#         # 각 target 마커 ID에 대해 체크
#         for marker_id in target_marker_ids:
#             if marker_id in detected_ids:
#                 # 마커가 감지되면 타이머 초기화
#                 marker_lost_times[marker_id] = None
#             else:
#                 # 마커가 감지되지 않으면 타이머 시작
#                 if marker_lost_times[marker_id] is None:
#                     marker_lost_times[marker_id] = time.time()  # 사라진 시간 기록
#                 elif time.time() - marker_lost_times[marker_id] > timeout_duration and time.time() - marker_lost_times[marker_id] < 5:
#                     # 마커가 사라진 후 timeout_duration 경과 시 perform_action 실행
#                     marker_lost_times[marker_id] = 6  # 타이머 초기화 (한 번만 실행)
                    
#                     marker_queue.put(marker_id)
#                     id=marker_queue.get()
#                     print(f"Marker ID {id} Action executed!")
                    
#                     if id == 5:
#                         robot.motion_home()
#                         # self.motion_home()
#                         # self.jig3_grab()
#                         # self.motion_home()
#                         # self.motion_check_sealing()
#                         # self.motion_place_capsule()
#                         # self.motion_grab_cup()
#                         # self.motion_make_icecream()
#                         # self.topping_2()
#                         # self.serve_jig3()
                    
#                     if id == 0:
#                         print("Aruco : 0")
#                         robot.motion_home()
                        
#                     if id == 7:
#                         print("Aruco : 7")
#                         robot.motion_home()
                
#         # 화면 출력
#         cv2.imshow("ArUco Marker Detection", frame)

#         # 'q' 키를 누르면 종료
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
        
#     # 정리
#     cap.release()
#     cv2.destroyAllWindows()
#     await websocket.close()


#### post code 
# @router.post("/") 
# async def get_topcam_id(topcam: TopcamCreate, service: topcamService = Depends(get_marker_id_service)):
#     id =service.get_marker_id(topcam)
#     return {"id": id}



# @router.get("/{ice_cream_id}", response_model=IceCreamResponse)
# async def get_ice_cream(ice_cream_id: int, service: IceCreamService = Depends(get_marker_id_service)):
#     ice_cream = service.get_ice_cream(ice_cream_id)
#     if ice_cream is None:
#         raise HTTPException(status_code=404, detail="Ice cream not found")
#     return ice_cream

# @router.put("/{ice_cream_id}", response_model=IceCreamResponse)
# async def update_ice_cream(ice_cream_id: int, ice_cream: IceCreamUpdate, service: IceCreamService = Depends(get_marker_id_service)):
#     updated = service.update_ice_cream(ice_cream_id, ice_cream)
#     if not updated:
#         raise HTTPException(status_code=404, detail="Ice cream not found or update failed")
#     return {**ice_cream.dict(exclude_unset=True), "id": ice_cream_id}

# @router.delete("/{ice_cream_id}", response_model=dict)
# async def delete_ice_cream(ice_cream_id: int, service: IceCreamService = Depends(get_marker_id_service)):
#     deleted = service.delete_ice_cream(ice_cream_id)
#     if not deleted:
#         raise HTTPException(status_code=404, detail="Ice cream not found or delete failed")
#     return {"message": "Ice cream deleted successfully"}
