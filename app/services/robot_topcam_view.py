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
import cv2
import numpy as np
from ultralytics import YOLO
from scipy.spatial import distance
import time
from gtts import gTTS  # gTTS 라이브러리 추가
import os
import threading

    
# import asyncio
# from gtts import gTTS
# import os
# import cv2
# import numpy as np
# from scipy.spatial import distance


class topcamService():
    
    async def get_topcam_id():
        
        # ArUco 마커 사전 및 파라미터 초기화
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
        parameters = cv2.aruco.DetectorParameters()
        cap = cv2.VideoCapture(0)
        # 감지할 마커 ID와 타이머 초기화
        target_marker_ids = {0, 5, 7}
        marker_lost_times = {marker_id: None for marker_id in target_marker_ids}
        timeout_duration = 3  # 감지 안 된 상태를 확인할 시간 (초)
        while cap.isOpened():
            ret, frame = await asyncio.to_thread(cap.read)
            if not ret:
                break
            # Grayscale 변환
            gray = await asyncio.to_thread(cv2.cvtColor, frame, cv2.COLOR_BGR2GRAY)
            # ArUco 마커 감지
            def detect_markers():
                return cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
            corners, ids, _ = await asyncio.to_thread(detect_markers)
            detected_ids = set(ids.flatten()) if ids is not None else set()
            # 감지되지 않은 마커 처리
            for marker_id in target_marker_ids:
                if marker_id in detected_ids:
                    # 마커가 감지되면 타이머 초기화
                    marker_lost_times[marker_id] = None
                else:
                    # 마커가 감지되지 않으면 타이머 시작
                    if marker_lost_times[marker_id] is None:
                        marker_lost_times[marker_id] = time.time()  # 사라진 시간 기록
                    elif time.time() - marker_lost_times[marker_id] > timeout_duration:
                        # 타임아웃 경과 시 ID 출력
                        print(f"Marker ID {marker_id} not detected!")
                        # 실행 완료 후 타이머 초기화
                        marker_lost_times[marker_id] = None
            
            # 'q' 키를 누르면 종료
            cv2.imshow("ArUco Marker Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
        # 자원 정리
        cap.release()
        cv2.destroyAllWindows()
        
        
    

# ## 백업, TTS 와 객체 인식 동시에 아직 안되는 상태 ( 실행 됨 ) #### 
    
# class topcamService():
    
#     def __init__(self, topcam_client=None):
#         """
#         yolo 모델 로드
#         """
#         # YOLOv8 모델 로드
#         self.model = YOLO('/home/hanse/xyz/FastAPI/BE/app/services/best.pt')  # 전체 객체 탐지 모델

#         # 웹캠 초기화
#         self.cap = cv2.VideoCapture(2)

#         # ROI 영역 정의 (지그 1, 2, 3의 좌표)
#         self.jig_positions = {
#             1: ((250, 35+20), (380, 140+20)),   # 지그 1: (좌상단, 우하단)
#             2: ((400, 30+20), (510, 132+20)),  # 지그 2
#             3: ((530, 30+20), (630, 135+20))   # 지그 3
#         }

#         # 프레임 처리 타이머 설정
#         self.frame_interval = 0.0  # 0.x초 간격으로 추론 (초당 약 x 프레임)
#         self.last_time = time.time()

#         # 메시지 상태 플래그
#         self.last_state = {"siling_detected": False, "distance_state": None}
        
#         self.topcam_client = topcam_client        
#         pass

#     # 음성 출력 함수
#     def speak_once(self, message, key):
#         """
#         gTTS를 사용하여 음성을 출력합니다.
#         """
#         # while self.last_state.get(key) != message:
#         if self.last_state.get(key) != message:
#             try:
#                 tts = gTTS(text=message, lang='ko')
#                 tts.save("./app/services/tts_text.mp3")
#                 os.system("mplayer ./app/services/tts_text.mp3")
#                 os.system("rm ./app/services/tts_text.mp3")
#                 self.last_state[key] = message
#             except Exception as e:
#                 print(f"음성 출력 오류: {e}")

#     # ROI 내 위치 확인 함수
#     def check_jig_position(self, mask_points):
#         """
#         마스크의 모든 좌표가 어느 지그에 완전히 들어있는지 확인
#         """
#         for jig_id, ((x1, y1), (x2, y2)) in self.jig_positions.items():
#             if all(x1 <= point[0] <= x2 and y1 <= point[1] <= y2 for point in mask_points):
#                 return jig_id
#         return None

#     async def yolo_run(self, websocket: WebSocket):
#         """
#         yolo 모델에서 person, robot_arm, siling, ice_cream을 추출, 및 거리계산 등 활용
#         """
#         while self.cap.isOpened():
#             ret, frame = self.cap.read()
#             if not ret:
#                 break

#             # 현재 시간이 마지막 추론 시간 + 프레임 간격보다 크면 추론 실행
#             if time.time() - self.last_time >= self.frame_interval:
#                 self.last_time = time.time()

#                 # YOLOv8 세그멘테이션 수행
#                 results = self.model.predict(source=frame, show=False)

#                 if results and results[0].masks:
#                     detected_objects = {"person": [], "robot_arm": [], "siling": [], "ice_cream": []}
#                     for i, mask in enumerate(results[0].masks.xy):
#                         cls = int(results[0].boxes.cls[i])
#                         conf = results[0].boxes.conf[i]
#                         label = self.model.names[cls]

#                         if conf < 0.4:
#                             continue  # 신뢰도 낮은 객체 무시

#                         # 필요한 객체만 필터링
#                         if label in detected_objects:
#                             mask_points = np.array(mask, dtype=np.int32)
#                             detected_objects[label].append(mask_points)

#                             # 화면 표시 (폴리곤 및 텍스트)
#                             color = {
#                                 "person": (0, 255, 0),      # 녹색
#                                 "robot_arm": (255, 0, 0),   # 파란색
#                                 "siling": (0, 0, 255),      # 빨간색
#                                 "ice_cream": (255, 255, 0)  # 노란색
#                             }.get(label, (255, 255, 255))
#                             x_center = int(np.mean(mask_points[:, 0]))  # x 중심 좌표
#                             y_center = int(np.mean(mask_points[:, 1]))  # y 중심 좌표
#                             cv2.polylines(frame, [mask_points], isClosed=True, color=color, thickness=2)
#                             cv2.putText(frame, label, (x_center, y_center - 10),
#                                         cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

#                             # "ice_cream"의 지그 위치 확인
#                             if label == "ice_cream":
#                                 jig_id = self.check_jig_position(mask_points)
#                                 if jig_id:
#                                     print(f"Ice Cream completely detected at Jig {jig_id}")
#                                     cv2.putText(frame, f"Jig {jig_id}", (x_center, y_center + 20),
#                                                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

#                     # "실링" 검출 여부 확인
#                     if detected_objects["siling"]:
#                         print("실링 검출: 실링을 제거해주세요!")  # 디버그 출력
#                         self.speak_once("실링을 제거해주세요!", "siling_detected")
#                     else:
#                         self.last_state["siling_detected"] = False  # 상태 초기화

#                     # 거리 계산 (사람과 로봇 팔 간 최소 거리)
#                     person_masks = detected_objects["person"]
#                     robot_arm_masks = detected_objects["robot_arm"]

#                     if person_masks and robot_arm_masks:
#                         min_distance = float('inf')
#                         for person_mask in person_masks:
#                             for robot_mask in robot_arm_masks:
#                                 dist = distance.cdist(person_mask, robot_mask).min()
#                                 min_distance = min(min_distance, dist)

#                         print(f"Closest distance between 'person' and 'robot_arm': {min_distance:.2f} pixels")

#                         # 거리 상태 출력
#                         if min_distance <= 15:
#                             self.speak_once("정지.", "distance_state")
#                         elif min_distance <= 70:
#                             self.speak_once("위험.", "distance_state")
#                         else:
#                             self.last_state["distance_state"] = None  # 안전 상태
#                     else:
#                         self.last_state["distance_state"] = None  # 거리 계산 없음

#                 # 지그 영역 표시
#                 for jig_id, ((x1, y1), (x2, y2)) in self.jig_positions.items():
#                     cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
#                     cv2.putText(frame, f"Jig {jig_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

#             # 화면에 표시
#             cv2.imshow('YOLOv8 Segmentation', frame)

#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
        
#         await websocket.send_text("YOLO detection running...")

#         # 자원 해제
#         self.cap.release()
#         cv2.destroyAllWindows()

#     def yolo_thread(self, websocket: WebSocket):
#         """
#         asyncio 루프 내에서 yolo_run을 실행
#         """
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         loop.run_until_complete(self.yolo_run(websocket))

#     def thread_run(self, websocket: WebSocket):
#         """
#         yolo와 tts를 함께 하기 위한 쓰레드
#         """
#         yolo_thread = threading.Thread(target=self.yolo_thread, args=(websocket,))
#         yolo_thread.start()

#         # tts_thread = threading.Thread(target=topcamService.speak_once)
#         # tts_thread.start()
        



# """
# 코드 수정중, TTS와 병렬로 캠 쓰는중 ( 버리는 코드 )
# """


# class DetectionService:
#     def __init__(self, topcam_client=None):
#         """
#         yolo 모델 로드
#         """
#         # YOLOv8 모델 로드
#         self.model = YOLO('/home/hanse/xyz/FastAPI/BE/app/services/best.pt')  # 전체 객체 탐지 모델

#         # 웹캠 초기화
#         self.cap = cv2.VideoCapture(2)

#         # ROI 영역 정의 (지그 1, 2, 3의 좌표)
#         self.jig_positions = {
#             1: ((250, 35+20), (380, 140+20)),   # 지그 1: (좌상단, 우하단)
#             2: ((400, 30+20), (510, 132+20)),  # 지그 2
#             3: ((530, 30+20), (630, 135+20))   # 지그 3
#         }

#         # 프레임 처리 타이머 설정
#         self.frame_interval = 0.0  # 0.x초 간격으로 추론 (초당 약 x 프레임)
#         self.last_time = time.time()

#         # 메시지 상태 플래그
#         self.last_state = {"siling_detected": False, "distance_state": None}
        
#         self.topcam_client = topcam_client        
#         pass

#         self.message_queue = asyncio.Queue()  # 메시지 큐 생성

#     # ROI 내 위치 확인 함수
#     def check_jig_position(self, mask_points):
#         """
#         마스크의 모든 좌표가 어느 지그에 완전히 들어있는지 확인
#         """
#         for jig_id, ((x1, y1), (x2, y2)) in self.jig_positions.items():
#             if all(x1 <= point[0] <= x2 and y1 <= point[1] <= y2 for point in mask_points):
#                 return jig_id
#         return None

#     async def speak_worker(self):
#         """TTS 메시지 큐를 처리하는 작업"""
#         while True:
#             message, key = await self.message_queue.get()  # 큐에서 메시지 꺼내기
#             if self.last_state.get(key) != message:
#                 try:
#                     tts = gTTS(text=message, lang='ko')
#                     tts.save("./app/services/tts_text.mp3")
#                     os.system("mplayer ./app/services/tts_text.mp3")
#                     os.system("rm ./app/services/tts_text.mp3")
#                     self.last_state[key] = message
#                 except Exception as e:
#                     print(f"음성 출력 오류: {e}")
#             self.message_queue.task_done()  # 작업 완료 처리

#     async def yolo_run(self, websocket):
#         """YOLO 모델 실행 및 TTS 메시지 큐에 작업 추가"""
#         asyncio.create_task(self.speak_worker())  # TTS 워커 실행

#         while self.cap.isOpened():
#             ret, frame = self.cap.read()
#             if not ret:
#                 break

#             if time.time() - self.last_time >= self.frame_interval:
#                 self.last_time = time.time()
#                 results = self.model.predict(source=frame, show=False)

#                 if results and results[0].masks:
#                     detected_objects = {"person": [], "robot_arm": [], "siling": [], "ice_cream": []}
#                     for i, mask in enumerate(results[0].masks.xy):
#                         cls = int(results[0].boxes.cls[i])
#                         conf = results[0].boxes.conf[i]
#                         label = self.model.names[cls]

#                         if conf < 0.4:
#                             continue

#                         if label in detected_objects:
#                             mask_points = np.array(mask, dtype=np.int32)
#                             detected_objects[label].append(mask_points)

#                     if detected_objects["siling"]:
#                         print("실링 검출: 실링을 제거해주세요!")
#                         await self.message_queue.put(("실링을 제거해주세요!", "siling_detected"))
#                     else:
#                         self.last_state["siling_detected"] = False

#                     person_masks = detected_objects["person"]
#                     robot_arm_masks = detected_objects["robot_arm"]

#                     if person_masks and robot_arm_masks:
#                         min_distance = float('inf')
#                         for person_mask in person_masks:
#                             for robot_mask in robot_arm_masks:
#                                 dist = distance.cdist(person_mask, robot_mask).min()
#                                 min_distance = min(min_distance, dist)

#                         print(f"Closest distance: {min_distance:.2f} pixels")
#                         if min_distance <= 15:
#                             await self.message_queue.put(("정지.", "distance_state"))
#                         elif min_distance <= 70:
#                             await self.message_queue.put(("위험.", "distance_state"))
#                         else:
#                             self.last_state["distance_state"] = None

#             cv2.imshow('YOLOv8 Segmentation', frame)

#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break

#         await websocket.send_text("YOLO detection running...")
#         self.cap.release()
#         cv2.destroyAllWindows()
    
    
#     def yolo_thread(self, websocket: WebSocket):
#         """
#         asyncio 루프 내에서 yolo_run을 실행
#         """
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         loop.run_until_complete(self.yolo_run(websocket))

#     def thread_run(self, websocket: WebSocket):
#         """
#         yolo와 tts를 함께 하기 위한 쓰레드
#         """
#         yolo_thread = threading.Thread(target=self.yolo_thread, args=(websocket,))
#         yolo_thread.start()

#         # tts_thread = threading.Thread(target=topcamService.speak_once)
#         # tts_thread.start()


