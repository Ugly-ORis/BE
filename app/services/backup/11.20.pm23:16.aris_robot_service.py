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
from gtts import gTTS  # gTTS 라이브러리 추가
from scipy.spatial import distance
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
from threading import Thread, Event
from queue import Queue
from queue import Empty

RobotMain.pprint('xArm-Python-SDK Version:{}'.format(version.__version__))
arm = XArmAPI('192.168.1.184', baud_checkset=False)
robot = RobotMain(arm)


class RobotService():
    def __init__(self, robot_client):
        self.robot_client = robot_client
        self.last_spoken = {}
        self.pixel_distance = 100
        self.number = 0

    def speak_once(self, marker_queue: Queue):
        """
        gTTS를 사용하여 음성을 출력
        같은 메시지는 10초 이내에 중복 출력되지 않음
        다른 메시지는 바로 출력 가능
        """
        number = marker_queue.get()  # 큐에서 메시지 가져오기
        
        if number == 1:
            message = "실링을 제거 해주세요. 아이스크림을 제자리에 돌려 놓습니다"
            
            while message :
                start_time = time.time()
                # 메시지 출력 시간 체크
                if message in self.last_spoken:
                    end_time = start_time - self.last_spoken[message]
                    if end_time < 10:  # 10초 이내에 동일 메시지 반복 방지
                        return

                print(f"Speaking: {message}")
                tts = gTTS(text=message, lang='ko')
                tts.save("tts_text.mp3")
                os.system("mplayer tts_text.mp3")  # 음성 재생
                os.remove("tts_text.mp3")  # 음성 파일 삭제

                self.last_spoken[message] = start_time  # 메시지와 시간 기록



    
    ########################################################
    
    # def speak_once(self, message):
    #     """
    #     gTTS를 사용하여 음성을 출력
    #     """
    #     while message:
    #         tts = gTTS(text=message, lang='ko')
    #         tts.save("tts_text.mp3")
    #         os.system("mplayer tts_text.mp3")
    #         os.system("rm tts_text.mp3")


    def robot_action(self, marker_queue: Queue):
        """
        토핑과 지그위에 올려둔 캡슐을 인지하여 로봇이 동작하는 로직
        """
        
        robot.motion_home_left()
        time.sleep(2)
        jig_id = 2                  ## 임시
        topping_ids = 2             ## 임시
        sealing_detect = 1          ## 임시
        
        
        if jig_id == 1:
            robot.jig1_grab()
            robot.motion_home_left()
            robot.motion_check_sealing()
            
            if sealing_detect == 1:
                self.number = 1
                marker_queue.put(self.number)
                robot.jig1_back()
                robot.motion_home_left()
            
            elif topping_ids == 0:
                robot.motion_grab_capsule()
                robot.motion_grab_cup()
                robot.motion_make_icecream()
                robot.topping_0()
                robot.serve_jig1()
                robot.motion_trash_capsule()
                robot.motion_home_left()
            elif topping_ids == 1:
                robot.motion_grab_capsule()
                robot.motion_grab_cup()
                robot.motion_make_icecream()
                robot.topping_1()
                robot.serve_jig1()
                robot.motion_trash_capsule()
                robot.motion_home_left()
                
            elif topping_ids == 2:
                robot.motion_grab_capsule()
                robot.motion_grab_cup()
                robot.motion_make_icecream()
                robot.topping_2()
                robot.serve_jig1()
                robot.motion_trash_capsule()
                robot.motion_home_left()
                    
        elif jig_id == 2:
            robot.jig2_grab()
            robot.motion_home_left()
            robot.motion_check_sealing()
            robot.motion_home_left()
            
            if sealing_detect == 1:
                message = "실링을 제거 해주세요. 아이스크림을 원위치에 돌려 놓습니다"
                self.speak_once(message)
                robot.jig2_back()
                robot.motion_home_left()
            
            elif topping_ids == 0:
                robot.motion_grab_capsule()
                robot.motion_grab_cup()
                robot.motion_make_icecream()
                robot.topping_0()
                robot.serve_jig2()
                robot.motion_trash_capsule()
                robot.motion_home_left()
            elif topping_ids == 1:
                robot.motion_grab_capsule()
                robot.motion_grab_cup()
                robot.motion_make_icecream()
                robot.topping_1()
                robot.serve_jig2()
                robot.motion_trash_capsule()
                robot.motion_home_left()
                
            elif topping_ids == 2:
                robot.motion_grab_capsule()
                robot.motion_grab_cup()
                robot.motion_make_icecream()
                robot.topping_2()
                robot.serve_jig2()
                robot.motion_trash_capsule()
                robot.motion_home_left()
        
        elif jig_id == 3:
            robot.jig3_grab()
            robot.motion_home_left()
            robot.motion_check_sealing()
            robot.motion_home_left()
            
            if sealing_detect == 1:
                message = "실링을 제거 해주세요. 아이스크림을 원위치에 돌려 놓습니다"
                self.speak_once(message)
                robot.jig3_back()
                robot.motion_home_left()
            
            elif topping_ids == 0:
                robot.motion_grab_capsule()
                robot.motion_grab_cup()
                robot.motion_make_icecream()
                robot.topping_0()
                robot.serve_jig3()
                robot.motion_trash_capsule()
                robot.motion_home_left()
            elif topping_ids == 1:
                robot.motion_grab_capsule()
                robot.motion_grab_cup()
                robot.motion_make_icecream()
                robot.topping_1()
                robot.serve_jig3()
                robot.motion_trash_capsule()
                robot.motion_home_left()
                
            elif topping_ids == 2:
                robot.motion_grab_capsule()
                robot.motion_grab_cup()
                robot.motion_make_icecream()
                robot.topping_2()
                robot.serve_jig3()
                robot.motion_trash_capsule()
                robot.motion_home_left()

    def emergency(self):
        """
        사람 손(person)과 로봇(robot_arm) 객체의 pixel 거리가 가까워지면 로봇이 정지
        """
        count = 0
        
        while True:
            count += 1
            time.sleep(0.1)
            if 29 > count > 20:
                robot.emergency_stop() # pause
            elif count > 30:
                robot.emergency_resume()
                print("재가동")
                count = 0
        
        
        
        
        
        
        # while True:
        #     if self.pixel_distance <= 30:
        #         robot.emergency_stop() # pause
        #     elif self.pixel_distance > 60:
        #         robot.emergency_resume()
        #         print("재가동")
        #     time.sleep(0.5)  
                
    def run(self):
        """
        멀티스레드를 활용하여 로봇 동작, 긴급 정지 및 음성 출력을 관리
        """
        marker_queue = Queue(maxsize=100)
        
        robot_thread = threading.Thread(target=self.robot_action, args=(marker_queue, ))
        robot_thread.daemon = True 
        robot_thread.start()
        
        emergency_thread = threading.Thread(target=self.emergency)
        emergency_thread.daemon = True
        emergency_thread.start()

        speak_once_thread = threading.Thread(target=self.speak_once, args=(marker_queue, ))
        speak_once_thread.daemon = True
        speak_once_thread.start()
        
        
        # robot_thread = threading.Thread(target=RobotService.robot_action)
        # robot_thread.start()
        # emergency_thread = threading.Thread(target=RobotService.emergency)
        # emergency_thread.start()
        # speak_once_thread = threading.Thread(target=RobotService.speak_once)
        # speak_once_thread.start()














### gpt 코드 ( 안됨 )
# class RobotService:
#     def __init__(self, client: MilvusClient, robot_instance: RobotMain):
#         self.client = client
#         self.robot = robot_instance  # robot 객체를 주입
        
#     async def robot_action(self):
#         """
#         주문자 요청과 비전 처리에 따른 로봇 동작 기능
#         """
#         print("robot_action activated!")
#         if not self.robot:  # robot 객체 초기화 여부 확인
#             raise ValueError("Robot instance is not initialized")
#         await self.robot.run()  # 비동기 로봇 동작 실행
        
#     async def emergency(self):
#         """
#         사람 손이 가까워 졌을 때 멈추는 기능
#         """
#         print("emergency_stop")
#         if not self.robot:  # robot 객체 초기화 여부 확인
#             raise ValueError("Robot instance is not initialized")
#         await self.robot.emergency_stop()  # 비동기 긴급 정지 실행


### 내가 짠 코드 ( 안됨 )
# class RobotService(object):
#     def __init__(self, client: MilvusClient):
#         self.client = client
        
#     async def robot_action():
#         """
#         주문자 요청과 비전 처리에 따른 로봇 동작 기능
#         """
#         print("robot_action activated!")
#         await robot.run()
        
#     async def emergency():
#         """
#         사람 손이 가까워 졌을때 멈추는 기능
#         """
#         print("emergency_stop")
#         await robot.emergency_stop()
