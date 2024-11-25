import cv2
import numpy as np
from ultralytics import YOLO
from scipy.spatial import distance
import time
from gtts import gTTS  # gTTS 라이브러리 추가
import os


class test():
    def yolo_run():
        # YOLOv8 모델 로드
        model = YOLO('/home/hanse/xyz/FastAPI/BE/app/services/best.pt')  # 전체 객체 탐지 모델

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

        # 메시지 상태 플래그
        last_state = {"siling_detected": False, "distance_state": None}

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

                        print(f"Closest distance between 'person' and 'robot_arm': {min_distance:.2f} pixels")

                        # 거리 상태 출력
                        if min_distance <= 5:
                            print("hi")
                        elif min_distance <= 40:
                            print("hi")
                        else:
                            last_state["distance_state"] = None  # 안전 상태
                    else:
                        last_state["distance_state"] = None  # 거리 계산 없음

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
        
if __name__ == "__main__":
    yolo = test
    yolo.yolo_run()