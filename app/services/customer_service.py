from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
from ultralytics import YOLO

# =====

import os, cv2
import numpy as np
from collections import deque
from datetime import datetime

import mediapipe as mp

import torch
import torch.nn.functional as F
from torchvision import transforms
from facenet_pytorch import InceptionResnetV1

from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam

from app.utils.id_manager import IDManager
from app.db.milvus_client import MilvusClient
from typing import Optional

class CustomerService:
    """
    고객 정보 서비스 클래스
    """

    def __init__(self, customer_client: MilvusClient):
        self.client = customer_client
        self.mtcnn = MTCNN()
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval()
        self.model = YOLO("yolo11x.pt")  
        self.id_manager = IDManager()
        self.id_manager.initialize_default_ids(["Customer"])

    def get_customers(self, offset: int, limit: int):
        results = self.client.collection.query(
            expr="", 
            output_fields=["customer_id", "name", "phone_last_digits", "created_at"], 
            limit=offset + limit 
        )
        
        return results[offset:offset + limit]

    def get_feature(self, img: Image.Image) -> np.ndarray:
        """
        얼굴 이미지로부터 특징 벡터 추출
        """
        img_cropped = self.mtcnn(img)
        if img_cropped is None:
            raise ValueError("얼굴을 감지할 수 없습니다.")
        image_vector = self.resnet(img_cropped.unsqueeze(0))
        return image_vector.detach().cpu().numpy().astype(np.float32)

    def get_similarity(self, origin_feature: np.ndarray, new_feature: np.ndarray) -> str:
        """
        두 특징 벡터 간의 코사인 유사도를 계산하고 결과에 따라 메시지를 반환
        """
        similarity = float(F.cosine_similarity(torch.tensor(origin_feature), torch.tensor(new_feature), dim=-1).mean())
        similarity_percentage = similarity * 100
        print(f"유사도: {similarity_percentage:.2f}%")

        if similarity >= 0.8:
            return "같은 사람입니다."
        elif similarity >= 0.6:
            return "얼굴을 좀 더 정확히 보여주세요."
        else:
            return "다른 사람으로 판단됩니다."

    def track_and_get_feature(self) -> np.ndarray:
        """
        카메라 피드를 열어 사용자가 선택한 얼굴의 특징 벡터를 반환
        """
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 420)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
        selected_face_vector = None
        click_x, click_y = -1, -1
        frame_skip = 5
        frame_count = 0

        def mouse_callback(event, x, y, flags, param):
            nonlocal click_x, click_y
            if event == cv2.EVENT_LBUTTONDOWN:
                click_x, click_y = x, y

        cv2.namedWindow("Human Tracking")
        cv2.setMouseCallback("Human Tracking", mouse_callback)

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            if frame_count % frame_skip == 0:
                results = self.model.track(frame, classes=0, conf=0.5, iou=0.8, persist=True)
                boxes = results[0].boxes.xywh.cpu() if results and results[0] else []
            frame_count += 1

            for box in boxes:
                bx, by, bw, bh = box
                sx, ex = int(bx - bw / 2), int(bx + bw / 2)
                sy, ey = int(by - bh / 2), int(by + bh / 2)

                if sx < click_x < ex and sy < click_y < ey:
                    face_img = Image.fromarray(cv2.cvtColor(frame[sy:ey, sx:ex], cv2.COLOR_BGR2RGB))
                    selected_face_vector = self.get_feature(face_img)
                    click_x, click_y = -1, -1 
                    break

                cv2.rectangle(frame, (sx, sy), (ex, ey), color=(255, 0, 0), thickness=2)

            cv2.imshow("Human Tracking", frame)
            if cv2.waitKey(1) & 0xFF == ord("q") or selected_face_vector is not None:
                break

        cap.release()
        cv2.destroyAllWindows()
        return selected_face_vector

    def search_customer(self, image_vector, threshold: float = 0.7) -> dict:
        """
        Milvus DB에서 특정 특징 벡터와 유사한 고객을 검색하고, 유사도에 따라 메시지 반환
        """
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = self.client.collection.search(
            data=[image_vector.flatten().astype(np.float32).tolist()],
            anns_field="image_vector",
            param=search_params,
            limit=1,
            output_fields=["image_vector", "name"]
        )
        if results and results[0]:
            matched_customer = results[0][0]
            match_vector = np.array(matched_customer.entity.get("image_vector"), dtype=np.float32)
            similarity_message = self.get_similarity(image_vector, match_vector)
            return {"name": matched_customer.entity.get("name"), "message": similarity_message}

        return {"message": "No matching customer found."}

    def insert_customer(self, image_vector, name: str, phone_last_digits: str):
        """
        DB에 새 고객 정보 저장
        """
        customer_id = self.id_manager.get_next_id("Customer")
        entities = [
            [customer_id],
            image_vector,
            [name],
            [phone_last_digits],
            [datetime.now().__str__()]
        ]
        
        try:
            insert_result = self.client.collection.insert(entities)
            self.client.collection.flush()
            return insert_result.primary_keys[0]
        except Exception as e:
            print(f"Insertion error: {e}")
            raise

    def get_customer(self, customer_id: int) -> Optional[dict]:
        """
        customer 데이터 가져오기
        """
        results = self.client.collection.query(f"customer_id == {customer_id}", output_fields=["id", "feature_vector", "customer_id", "name", "phone_last_digits", "created_at"])
        return results[0] if results else None

    def delete_customer(self, customer_id: int) -> bool:
        """
        customer 데이터 삭제
        """
        delete_result = self.client.collection.delete(f"customer_id == {customer_id}")
        self.client.collection.flush()
        self.client.collection.compact()
        return delete_result is not None
    
    def update_customer(self, customer_id: int, name: str, phone_last_digits: str):
        """
        customer update 구현
        new user의 face vector를 일시 저장 -> 이벤트 발생 (본인 확인) 
        -> new user에 id + 1을 하고 임시 저장된 face vector와 이름, 전화번호를 추가해서 새로 저장
        """
        customer_info = self.get_customer(customer_id)
        feature_vector = customer_info.get("feature_vector")  # -> list
        feature_vector = np.array(feature_vector, dtype=np.float32).reshape(1, 512)
        self.delete_customer(customer_id)
        self.insert_customer(feature_vector, name, phone_last_digits)