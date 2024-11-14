from fastapi import WebSocket
from app.schemas.topcam_schema import TopcamCreate
from app.db.milvus_client import MilvusClient
# from app.schemas.ice_cream_schema import IceCreamCreate, IceCreamUpdate
from typing import Optional
import cv2
import time
import numpy as np
from BE.xArm_Python_SDK.robot_action import RobotMain
from xarm.wrapper import XArmAPI
from xarm import version
import asyncio

RobotMain.pprint('xArm-Python-SDK Version:{}'.format(version.__version__))
arm = XArmAPI('192.168.1.184', baud_checkset=False)
robot = RobotMain(arm)

class topcamService():
    
    def __init__(self, client: MilvusClient):
        self.client = client
        
    async def get_marker_id(self, websocket: WebSocket):
        await websocket.accept()
        """
        아리스 상단 캠을 열어 아루코마커를 읽어 캡슐을 인식하기 위함
        """
        
        # ArUco 사전 (marker dictionary)와 marker size (예: 6x6 크기의 마커)
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
        parameters = cv2.aruco.DetectorParameters()
        # 웹캠 열기
        cap = cv2.VideoCapture(2)

        # 특정 마커 ID 설정 (이 ID의 마커가 사라졌을 때 트리거)
        target_marker_ids = {0,5,7}  # 사라짐을 감지할 마커 ID 집합
        marker_lost_times = {marker_id: None for marker_id in target_marker_ids}  # 각 마커의 사라짐 시간
        timeout_duration = 3  # 사라짐 확인 시간 (초)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Grayscale 변환
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # ArUco 마커 감지
            corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

            # 현재 감지된 마커 ID 목록을 집합으로 만듦
            detected_ids = set(ids.flatten()) if ids is not None else set()

            # 감지된 마커 그리기
            if ids is not None:
                cv2.aruco.drawDetectedMarkers(frame, corners, ids)

            # 각 target 마커 ID에 대해 체크
            for marker_id in target_marker_ids:
                if marker_id in detected_ids:
                    # 마커가 감지되면 타이머 초기화
                    marker_lost_times[marker_id] = None
                else:
                    # 마커가 감지되지 않으면 타이머 시작
                    if marker_lost_times[marker_id] is None:
                        marker_lost_times[marker_id] = time.time()  # 사라진 시간 기록
                    elif time.time() - marker_lost_times[marker_id] > timeout_duration and time.time() - marker_lost_times[marker_id] < 5:
                        # 마커가 사라진 후 timeout_duration 경과 시 perform_action 실행
                        marker_lost_times[marker_id] = 6  # 타이머 초기화 (한 번만 실행)
                        
                        # self.robot_action(self, marker_id)
                        if marker_id == 5:
                            await asyncio.to_thread(self.robot_action, marker_id)

            # 화면 출력
            cv2.imshow("ArUco Marker Detection", frame)

            # 'q' 키를 누르면 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                await websocket.close()
                break
        
        # 정리
        cap.release()
        cv2.destroyAllWindows()
        
    def robot_action(self, marker_id):
        if marker_id == 5:
            print("지그 3 캡슐 인식")
            robot.motion_home()
            
            
    # asyncio.run(get_marker_id())



################################
# RobotMain.pprint('xArm-Python-SDK Version:{}'.format(version.__version__))
# arm = XArmAPI('192.168.1.184', baud_checkset=False)
# robot = RobotMain(arm)

# class topcamService:

#     def __init__(self, client: MilvusClient):
#         self.client = client
        
#     async def get_marker_id(self, websocket: WebSocket):
#         await websocket.accept()
#         """
#         아리스 상단 캠을 열어 아루코마커를 읽어 캡슐을 인식하기 위함
#         """
        
#         # ArUco 사전 (marker dictionary)와 marker size (예: 6x6 크기의 마커)
#         aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
#         parameters = cv2.aruco.DetectorParameters()
#         # 웹캠 열기
#         cap = cv2.VideoCapture(2)

#         # 특정 마커 ID 설정 (이 ID의 마커가 사라졌을 때 트리거)
#         target_marker_ids = {0,5,7}  # 사라짐을 감지할 마커 ID 집합
#         marker_lost_times = {marker_id: None for marker_id in target_marker_ids}  # 각 마커의 사라짐 시간
#         timeout_duration = 3  # 사라짐 확인 시간 (초)
#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             # Grayscale 변환
#             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#             # ArUco 마커 감지
#             corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

#             # 현재 감지된 마커 ID 목록을 집합으로 만듦
#             detected_ids = set(ids.flatten()) if ids is not None else set()

#             # 감지된 마커 그리기
#             if ids is not None:
#                 cv2.aruco.drawDetectedMarkers(frame, corners, ids)

#             # 각 target 마커 ID에 대해 체크
#             for marker_id in target_marker_ids:
#                 if marker_id in detected_ids:
#                     # 마커가 감지되면 타이머 초기화
#                     marker_lost_times[marker_id] = None
#                 else:
#                     # 마커가 감지되지 않으면 타이머 시작
#                     if marker_lost_times[marker_id] is None:
#                         marker_lost_times[marker_id] = time.time()  # 사라진 시간 기록
#                     elif time.time() - marker_lost_times[marker_id] > timeout_duration and time.time() - marker_lost_times[marker_id] < 5:
#                         # 마커가 사라진 후 timeout_duration 경과 시 perform_action 실행
#                         marker_lost_times[marker_id] = 6  # 타이머 초기화 (한 번만 실행)
#                         # print(" 아이스크림 캡슐 인식1 : ", marker_id, (type(marker_id)))
#                         await self.robot_action(marker_id)

#                         # await asyncio.to_thread(self.robot_action, marker_id)

#             # 화면 출력
#             cv2.imshow("ArUco Marker Detection", frame)

#             # 'q' 키를 누르면 종료
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 await websocket.close()
#                 break
        
#         # 정리
#         cap.release()
#         cv2.destroyAllWindows()
        
#     async def robot_action(self, id):
#         print("hello")
        
        # if id == 5:
        #     print("지그 3 캡슐 인식")
        #     # await asyncio.to_thread(robot.motion_home())
        #     robot.motion_home()

            # await robot.jig3_grab()
            # await robot.motion_home()
            # await robot.motion_check_sealing()
            # await robot.motion_place_capsule()
            # await robot.motion_grab_cup()
            # await robot.motion_make_icecream()
            # await robot.topping_2()
            # await robot.serve_jig3()
        
        # if marker_id == 7:
        #     print("지그 2 캡슐 인식")
        #     # robot.motion_home()
            
        # if marker_id == 0:
        #     print("지그 1 캡슐 인식")
        #     # robot.motion_home()
            
    
    

    # def create_ice_cream(self, ice_cream_data: IceCreamCreate) -> int:
    #     entities = [
    #         [ice_cream_data.name],
    #         [ice_cream_data.flavor],
    #         [ice_cream_data.price],
    #         [ice_cream_data.stock]
    #     ]
    #     insert_result = self.client.collection.insert(entities)
    #     self.client.collection.flush()
    #     return insert_result.primary_keys[0]

    # def get_ice_cream(self, ice_cream_id: int) -> Optional[dict]:
    #     result = self.client.collection.query(f"id == {ice_cream_id}")
    #     return result[0] if result else None

    # def update_ice_cream(self, ice_cream_id: int, ice_cream_data: IceCreamUpdate) -> bool:
    #     update_fields = {k: v for k, v in ice_cream_data.dict().items() if v is not None}
    #     return self.client.collection.update(ice_cream_id, update_fields)

    # def delete_ice_cream(self, ice_cream_id: int) -> bool:
    #     return self.client.collection.delete(f"id == {ice_cream_id}")
