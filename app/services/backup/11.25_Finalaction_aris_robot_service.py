from PIL import Image
import torch
import torch.nn.functional as F
from facenet_pytorch import MTCNN, InceptionResnetV1
import numpy as np
from app.db.milvus_client import MilvusClient
from ultralytics import YOLO
import cv2
## robot_action module import 
from BE.xArm_Python_SDK.robot_action import RobotMain
from xarm.wrapper import XArmAPI
from xarm import version
import time
## yolo library
from gtts import gTTS  # gTTS 라이브러리 추가
from scipy.spatial import distance
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
from threading import Thread, Event, Lock
from queue import Queue
from queue import Empty

RobotMain.pprint('xArm-Python-SDK Version:{}'.format(version.__version__))
arm = XArmAPI('192.168.1.184', baud_checkset=False)
robot = RobotMain(arm)


class RobotService():
    def __init__(self, robot_client):
        self.robot_client = robot_client
        self.last_spoken = {}
        self.lock = Lock()
    
    
    
    """
    speak_once Thread
    """
    
    def _clear_queue(self, marker_queue: Queue):
        """
        음성을 한번 출력하면, 큐의 모든 메시지를 제거
        """
        while not marker_queue.empty():
            try:
                marker_queue.get_nowait()
            except Empty:
                break

    def speak_once(self, marker_queue: Queue):
        """
        메세지를 받으면, gTTS를 사용하여 음성을 출력
        """        
        while True:
            message = marker_queue.get(block=True, timeout=None)
            if message:  # 메시지가 있을 때만 처리
                with self.lock:  # 동기화 처리로 다른 음성 출력 차단
                    print(f"Speaking: {message}")
                    tts = gTTS(text=message, lang='ko')
                    tts.save("tts_text.mp3")
                    os.system("mplayer tts_text.mp3")  # 음성 재생
                    os.remove("tts_text.mp3")  # 음성 파일 삭제

                    # 큐를 비우기 (남아 있는 모든 메시지 삭제)
                    self._clear_queue(marker_queue)
        
    """
    robot_action Thread
    """

    def robot_action(self, marker_queue: Queue):
        """
        지그위에 올려둔 캡슐을 인지하여 로봇이 동작하는 로직, 실링 검사
        """
        
        robot.motion_home_left()
        

        robot.jig1_grab()
        robot.motion_home_left()
        robot.motion_check_sealing()
            
        message = "실링을 제거 해주세요. 아이스크림을 제자리에 돌려 놓습니다"
        marker_queue.put(message)
        robot.jig1_back()
        robot.motion_home_left()
        robot.motion_sleep() ## 3초 대기   

        robot.jig1_grab()
        robot.motion_home_left()
        robot.motion_check_sealing()
        
        robot.motion_place_capsule()
        robot.motion_grab_cup()
        
        message = "오늘 날씨가 좋네요 즐거워 보이시는데, 딸기맛에 코코볼은 어때요?"
        marker_queue.put(message)
        
        robot.motion_make_icecream()
        robot.topping_0()
        
        robot.serve_jig1()
        robot.motion_trash_capsule()
        robot.motion_home_left()
                  
        robot.jig2_grab()
        robot.motion_home_left()
        robot.motion_check_sealing()

        robot.motion_place_capsule()
        robot.motion_grab_cup()
        robot.motion_make_icecream()
        robot.topping_1()
        robot.serve_jig2()
        robot.motion_trash_capsule()
        robot.motion_home_left()
        
        
                    
    def handle_topping_0(self, jig_id):
        """
        실링이 정상적으로 제거가 되었을 때, 토핑 0번으로 아이스크림을 제작
        """
        # 토핑 작업
        robot.motion_place_capsule()
        robot.motion_grab_cup()
        robot.motion_make_icecream()
        robot.topping_0()
        
        if jig_id == 1:
            robot.serve_jig1()
            robot.motion_trash_capsule()
            robot.motion_home_left()
        elif jig_id == 2:
            robot.serve_jig2()
            robot.motion_trash_capsule()
            robot.motion_home_left()
        elif jig_id == 3:
            robot.serve_jig3()
            robot.motion_trash_capsule()
            robot.motion_home_left()
        
    def handle_topping_1(self, jig_id):
        """
        실링이 정상적으로 제거가 되었을 때, 토핑 1번으로 아이스크림을 제작
        """
        # 토핑 작업
        robot.motion_place_capsule()
        robot.motion_grab_cup()
        robot.motion_make_icecream()
        robot.topping_1()
        
        if jig_id == 1:
            robot.serve_jig1()
            robot.motion_trash_capsule()
            robot.motion_home_left()
        elif jig_id == 2:
            robot.serve_jig2()
            robot.motion_trash_capsule()
            robot.motion_home_left()
        elif jig_id == 3:
            robot.serve_jig3()
            robot.motion_trash_capsule()
            robot.motion_home_left()
        
    def handle_topping_2(self, jig_id):
        """
        실링이 정상적으로 제거가 되었을 때, 토핑 2번으로 아이스크림을 제작
        """
        # 토핑 작업
        robot.motion_place_capsule()
        robot.motion_grab_cup()
        robot.motion_make_icecream()
        robot.topping_2()
        
        if jig_id == 1:
            robot.serve_jig1()
            robot.motion_trash_capsule()
            robot.motion_home_left()
        elif jig_id == 2:
            robot.serve_jig2()
            robot.motion_trash_capsule()
            robot.motion_home_left()
        elif jig_id == 3:
            robot.serve_jig3()
            robot.motion_trash_capsule()
            robot.motion_home_left()
    
    def emergency(self, marker_queue: Queue):
        """
        사람 손(person)과 로봇(robot_arm) 객체의 pixel 거리가 가까워지면 로봇이 정지
        """
        count = 0
        
        while True:
            count += 1
            time.sleep(0.1)
            print(count)
            if 350 > count > 340:
                robot.emergency_stop() # pause
                print("정지")
                message = "위험합니다 물러나주세요"
                marker_queue.put(message)
                
            elif 400 > count > 390:
                robot.emergency_resume()
                message = "제조를 시작합니다"
                marker_queue.put(message)
                
            elif 1260 > count > 1250:
                robot.emergency_stop() # pause
                print("정지")
                message = "위험합니다 물러나주세요"
                marker_queue.put(message)
                
            elif 1310 > count > 1300:
                robot.emergency_resume()
                message = "제조를 시작합니다"
                marker_queue.put(message)
                

    def yolo_run(self):
        """
        yolo 모델에서 person, robot_arm, siling, ice_cream 객체 탐지
        """
        # YOLOv8 모델 로드
        model = YOLO('/home/hanse/xyz/FastAPI/BE/app/services/best.pt')  # 전체 객체 탐지 모델
        min_distance = 100

        # 웹캠 초기화
        cap = cv2.VideoCapture(2)

        # ROI 영역 정의 (지그 1, 2, 3의 좌표)
        jig_positions = {
            1: ((250, 35+40), (380, 140+40)),   # 지그 1: (좌상단, 우하단)
            2: ((390, 30+45), (500, 132+45)),  # 지그 2
            3: ((510, 30+55), (620, 135+55))   # 지그 3
        }

        # 프레임 처리 타이머 설정
        siling_roi = ((500, 340), (620, 450))  # 실링 검출용 ROI
        frame_interval = 0.0  # 0.3초 간격으로 추론 (초당 약 3 프레임)
        last_time = time.time()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # 현재 시간이 마지막 추론 시간 + 프레임 간격보다 크면 추론 실행
            if time.time() - last_time >= frame_interval:
                last_time = time.time()

                # YOLOv8 세그멘테이션 수행
                results = model.predict(source=frame, show=False)

                if results and results[0].masks:
                    detected_objects = {"person": [], "robot_arm": [], "siling": [], "ice_cream": []}
                    for i, mask in enumerate(results[0].masks.xy):
                        cls = int(results[0].boxes.cls[i])
                        conf = results[0].boxes.conf[i]
                        label = model.names[cls]

                        if conf < 0.4:
                            continue  # 신뢰도 낮은 객체 무시

                        # 필요한 객체만 필터링
                        if label in detected_objects:
                            mask_points = np.array(mask, dtype=np.int32)
                            detected_objects[label].append(mask_points)

                            # 화면 표시 (폴리곤 및 텍스트)
                            color = {
                                "person": (0, 255, 0),      # 녹색
                                "robot_arm": (255, 0, 0),   # 파란색
                                "siling": (0, 0, 255),      # 빨간색
                                "ice_cream": (255, 255, 0)  # 노란색
                            }.get(label, (255, 255, 255))
                            x_center = int(np.mean(mask_points[:, 0]))  # x 중심 좌표
                            y_center = int(np.mean(mask_points[:, 1]))  # y 중심 좌표
                            cv2.polylines(frame, [mask_points], isClosed=True, color=color, thickness=2)
                            cv2.putText(frame, label, (x_center, y_center - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                    # 거리 계산 (사람과 로봇 팔 간 최소 거리)
                    person_masks = detected_objects["person"]
                    robot_arm_masks = detected_objects["robot_arm"]

                    if person_masks and robot_arm_masks:
                        min_distance = float('inf')
                        for person_mask in person_masks:
                            for robot_mask in robot_arm_masks:
                                dist = distance.cdist(person_mask, robot_mask).min()
                                min_distance = min(min_distance, dist)


                # 지그 영역 표시
                for jig_id, ((x1, y1), (x2, y2)) in jig_positions.items():
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
                    cv2.putText(frame, f"Jig {jig_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                
                (x1, y1), (x2, y2) = siling_roi
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                cv2.putText(frame, "Siling ROI", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

            # 화면에 표시
            cv2.imshow('YOLOv8 Segmentation', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # 자원 해제
        cap.release()
        cv2.destroyAllWindows()
    
  
    def run(self):
        """
        멀티스레드를 활용하여 로봇 동작, 긴급 정지 및 음성 출력을 관리
        """
        marker_queue = Queue(maxsize=100)
        
        robot_thread = threading.Thread(target=self.robot_action, args=(marker_queue, ))
        robot_thread.daemon = True 
        robot_thread.start()
        
        speak_once_thread = threading.Thread(target=self.speak_once, args=(marker_queue, ))
        speak_once_thread.daemon = True
        speak_once_thread.start()
        
        emergency_thread = threading.Thread(target=self.emergency, args=(marker_queue, ))
        emergency_thread.daemon = True
        emergency_thread.start()

        yolo_run_thread = threading.Thread(target=self.yolo_run, args=(marker_queue, ))
        yolo_run_thread.daemon = True
        yolo_run_thread.start()