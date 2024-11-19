import os, cv2
import numpy as np
from collections import deque
from datetime import datetime

import mediapipe as mp

import torch
import torch.nn.functional as F
from torchvision import transforms
from facenet_pytorch import InceptionResnetV1

from tensorflow import keras
from keras.layers import Dense
from keras.models import Sequential, load_model

from keras.models import load_model, Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from keras.optimizers import Adam

from app.utils.id_manager import IDManager
from app.db.milvus_client import MilvusClient
from typing import Optional


class CustomerService:
    """
    고객 정보 서비스 클래스
    """
    def __init__(self, client: MilvusClient):
        self.client = client
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval()
        self.id_manager = IDManager()
        self.id_manager.initialize_default_ids(["Customer_Prac"])

        # 감정 모델 로드
        self.emotion_model = load_model('emotion_model.h5') if 'emotion_model.h5' else self.create_emotion_model()
        # MediaPipe Face Mesh 설정
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

        # 랜드마크 및 연결선 스타일 설정
        self.landmark_style = self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)
        self.connection_style = self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)

        # 감정 레이블 및 가중치 설정
        self.emotion_labels = ['Happy', 'Sad', 'Surprised', 'Angry', 'Fearful', 'Disgusted', 'Neutral', 'Calm']
        self.emotion_weights = [1.01, 0.0, 0.0, 1.1, 0.0, 0.0, 1.1, 0.0]
        self.emotion_history = deque(maxlen=15)

    def create_emotion_model(self, input_shape=(64, 64, 1)):
        """
        감정 인식 모델 생성 함수
        """
        model = Sequential([
            Conv2D(64, (3, 3), activation='relu', input_shape=input_shape),
            MaxPooling2D((2, 2)),
            Conv2D(128, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            Conv2D(256, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            Flatten(),
            Dense(256, activation='relu'),
            Dropout(0.5),
            Dense(len(self.emotion_labels), activation='softmax')
        ])
        model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])
        return model

    def preprocess_face_patch(self, face_patch: np.ndarray) -> np.ndarray:
        """
        얼굴 전처리 함수
        """
        gray_face = cv2.cvtColor(face_patch, cv2.COLOR_BGR2GRAY)
        resized_face = cv2.resize(gray_face, (64, 64))
        face_patch = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(resized_face)
        return face_patch.reshape(1, 64, 64, 1) / 255.0

    def classify_face_shape_and_eyes(self, landmarks) -> str:
        """
        얼굴형 분류 및 눈 크기 계산 함수
        """
        chin_y, forehead_y = landmarks[152].y, landmarks[10].y
        jaw_width = abs(landmarks[234].x - landmarks[454].x)
        face_shape = "Square Face: Determined" if jaw_width / abs(forehead_y - chin_y) > 0.6 else "Oval Face: Calm"
        
        left_ear = (abs(landmarks[159].y - landmarks[145].y) + abs(landmarks[153].y - landmarks[144].y)) / (2 * abs(landmarks[133].x - landmarks[33].x))
        right_ear = (abs(landmarks[386].y - landmarks[374].y) + abs(landmarks[373].y - landmarks[380].y)) / (2 * abs(landmarks[263].x - landmarks[362].x))
        eye_size = "Large Eyes: Open" if (left_ear + right_ear) / 2 > 0.25 else "Small Eyes: Focused"
        return face_shape, eye_size

    def extract_face_region(self, landmarks, frame_shape: tuple) -> tuple:
        """
        얼굴 영역 추출 함수
        """
        ih, iw, _ = frame_shape
        key_points = [10, 152, 234, 454, 33, 263, 1]
        coords = [(int(landmarks[p].x * iw), int(landmarks[p].y * ih)) for p in key_points]
        x_coords, y_coords = zip(*coords)
        padding = 20
        return (max(0, min(x_coords) - padding), max(0, min(y_coords) - padding), min(iw, max(x_coords) + padding), min(ih, max(y_coords) + padding))

    def get_feature(self, frame: np.ndarray) -> np.ndarray:
        """
        얼굴 이미지로부터 특징 벡터 추출
        """
        if frame.dtype != 'uint8':
            frame = np.clip(frame, 0, 255).astype('uint8')

        transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((160, 160)),
            transforms.ToTensor()
        ])
        frame = transform(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  # -> torch.Tensor([3, 160, 160])
        return self.resnet(frame.unsqueeze(0)).detach().cpu().numpy().astype(np.float32)

    def get_similarity(self, origin_feature: np.ndarray, new_feature: np.ndarray) -> str:
        """
        두 특징 벡터 간의 코사인 유사도를 계산하고 결과에 따라 메시지를 반환
        """
        similarity = abs(float(F.cosine_similarity(torch.tensor(origin_feature), torch.tensor(new_feature), dim=-1).mean()))
        similarity_percentage = similarity * 100
        print(f"유사도: {similarity_percentage:.2f}%")

        if similarity >= 0.8:
            return "같은 사람입니다."
        elif similarity >= 0.6:
            return "얼굴을 좀 더 정확히 보여주세요."
        else:
            return "다른 사람으로 판단됩니다."

    def track_and_get_feature(self):  # -> np.ndarray
        """
        카메라 피드를 열어 사용자가 선택한 얼굴의 특징 벡터를 반환
        """
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 490)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 420)
        selected_face_vector = None

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                continue

            results = self.face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    landmarks = face_landmarks.landmark

                    # 얼굴 영역 추출
                    x_min, y_min, x_max, y_max = self.extract_face_region(landmarks, frame.shape)
                    face_patch = frame[y_min:y_max, x_min:x_max]
                    if face_patch.size == 0:
                        continue
                            
                    # 감정 예측
                    face_patch = self.preprocess_face_patch(face_patch)
                    emotion_prediction = self.emotion_model.predict(face_patch)[0]

                    # 감정별 가중치 적용 및 확률 재조정
                    emotion_prediction = (emotion_prediction * self.emotion_weights) / np.sum(emotion_prediction * self.emotion_weights)
                    emotion_final = self.emotion_labels[np.argmax(emotion_prediction)]
                    self.emotion_history.append(emotion_final)

                    # 최종 감정 출력
                    emotion_text = f'{emotion_final} ({np.max(emotion_prediction) * 100:.1f}%)'
                    cv2.putText(frame, f'Emotion: {emotion_text}', (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                    self.mp_drawing.draw_landmarks(frame, face_landmarks, self.mp_face_mesh.FACEMESH_CONTOURS, landmark_drawing_spec=self.landmark_style, connection_drawing_spec=self.connection_style)

                    # if 주문자가 맞습니까? yes -> getfeature 동작 -> DB 저장 ==============================
                    if (x_max - x_min) > 250 and (y_max - y_min) > 250:
                        try:
                            selected_face_vector = self.get_feature(face_patch)
                        except ValueError as E:
                            print(E)
                            print("얼굴을 감지할 수 없습니다====")
                            continue
                    else:
                        print("주문자는 더 가까이 와주세요====")
                    # =================================================================================

            success, buffer = cv2.imencode('.jpg', frame)
            if not success:
                continue
            
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n'
                )
        cap.release()
        return selected_face_vector

    def search_customer(self, feature_vector, threshold: float = 0.7) -> dict:
        """
        Milvus DB에서 특정 특징 벡터와 유사한 고객을 검색하고, 유사도에 따라 메시지 반환
        """
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = self.client.collection.search(
            data=[feature_vector.flatten().astype(np.float32).tolist()],
            anns_field="feature_vector",
            param=search_params,
            limit=1,
            output_fields=["feature_vector", "name"]
        )
        if results and results[0]:
            matched_customer = results[0][0]
            match_vector = np.array(matched_customer.entity.get("feature_vector"), dtype=np.float32)
            similarity_message = self.get_similarity(feature_vector, match_vector)
            return {"name": matched_customer.entity.get("name"), "message": similarity_message}

        return {"message": "No matching customer found."}

    def get_customer(self, customer_id: int) -> Optional[dict]:
        """
        customer 데이터 가져오기
        """
        results = self.client.collection.query(f"customer_id == {customer_id}", output_fields=["id", "feature_vector", "customer_id", "name", "phone_last_digits", "created_at"])
        return results[0] if results else None
    
    def delete_customer(self, customer_id: int) -> bool:
        """
        데이터 삭제
        """
        delete_result = self.client.collection.delete(f"customer_id == {customer_id}")
        self.client.collection.flush()
        self.client.collection.compact()
        return delete_result is not None

    def insert_customer(self, feature_vector, name: str, phone_last_digits: str):
        """
        DB에 새 고객 정보 저장 (= 업데이트 = 임의의 첫 데이터 삭제 후 저장)
        상황: 일단 new user로써 id를 받고 저장 -> 이벤트 발생 -> new user에 id + 1을 하고 vector 추출해서 저장
        1. new user의 feature를 tmp로 저장하고
        2. 그 id 정보 삭제하고 (delete구현)
        3. id+1에 사용자의 이름과 전화번호 뒷자리를 넣어서 고객 정보를 완성시켜서 collection에 다시 저장
        그럼 id가 1,2,3,4,5 로 생성되는게 아니라 하나씩 건너서 2,4,6,8 식으로 저장될거임
        """
        customer_id = self.id_manager.get_next_id("Customer")
        entities = [
            [customer_id],
            feature_vector,
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

    def update_customer(self, customer_id: int, name: str, phone_last_digits: str):
            """
            update 최종 구현
            """
            customer_info = self.get_customer(customer_id)
            feature_vector = customer_info.get("feature_vector")  # -> list
            feature_vector = np.array(feature_vector, dtype=np.float32).reshape(1, 512)
            self.delete_customer(customer_id)
            self.insert_customer(feature_vector, name, phone_last_digits)
    