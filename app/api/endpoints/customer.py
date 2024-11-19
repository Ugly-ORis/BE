from fastapi import FastAPI, Query, APIRouter, Depends, WebSocket, HTTPException
from app.schemas.customer_schema import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services.customer_service import CustomerService
from app.api.dependencies import customer_client
import numpy as np
import cv2
from PIL import Image
from typing import List

def get_customer_service() -> CustomerService:
    return CustomerService(customer_client)

router = APIRouter()

@router.get("/", response_model=List[CustomerResponse])
async def get_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: CustomerService = Depends(get_customer_service)
):
    """
    페이징된 판매 상품 목록을 가져오는 API.
    """
    offset = (page - 1) * page_size
    customers = service.get_customers(offset=offset, limit=page_size)
    
    if not customers:
        raise HTTPException(status_code=404, detail="No Customers found.")
    
    return customers

@router.post("/", response_model=dict, summary="새 고객 추가")
async def create_customer(
    customer: CustomerCreate,
    service: CustomerService = Depends(get_customer_service)
) -> dict:
    """
    새로운 고객 정보를 Milvus 데이터베이스에 추가

    - **customer**: 추가할 고객 정보 (이름, 특징 벡터, 전화번호 뒷자리 등)
    - **response**: 생성된 고객 ID와 성공 메시지
    """
    customer_id = service.insert_customer(customer)
    return {"customer_id": customer_id, "message": "Customer created successfully."}

@router.websocket("/capture")
async def capture_face(websocket: WebSocket, service: CustomerService = Depends(get_customer_service)):
    await websocket.accept()
    cap = cv2.VideoCapture(0)
    click_x, click_y = -1, -1
    selected_face_vector = None

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # YOLO 모델로 사람 추적 및 경계 상자 그리기
            results = service.model.track(frame, classes=0, conf=0.5, iou=0.8, persist=True)
            boxes = results[0].boxes.xywh.cpu() if results and results[0] else []

            for box in boxes:
                bx, by, bw, bh = box
                sx, ex = int(bx - bw / 2), int(bx + bw / 2)
                sy, ey = int(by - bh / 2), int(by + bh / 2)
                cv2.rectangle(frame, (sx, sy), (ex, ey), color=(255, 0, 0), thickness=2)

                # 클릭된 좌표가 경계 상자 안에 있으면 얼굴 벡터 추출
                if sx < click_x < ex and sy < click_y < ey:
                    face_img = Image.fromarray(cv2.cvtColor(frame[sy:ey, sx:ex], cv2.COLOR_BGR2RGB))
                    selected_face_vector = service.get_feature(face_img)
                    click_x, click_y = -1, -1  # 클릭 위치 초기화
                    break

            # 현재 프레임 전송
            _, buffer = cv2.imencode(".jpg", frame)
            await websocket.send_bytes(buffer.tobytes())

            # 좌표 수신 및 업데이트
            try:
                data = await websocket.receive_json()
                click_x, click_y = data.get("x", -1), data.get("y", -1)
            except Exception as e:
                print("Error receiving JSON:", e)
                break  # 예외가 발생하면 반복을 중단하고 루프 종료

            # 얼굴 벡터 검색 및 결과 전송
            if selected_face_vector is not None:
                result = service.search_customer(selected_face_vector)
                if result.get("name"):
                    await websocket.send_json({"message": f"Welcome back, {result['name']}!"})
                else:
                    customer_id = service.insert_customer(selected_face_vector, "New User", "0000")
                    await websocket.send_json({"message": "New user created.", "customer_id": customer_id})
                break  # 얼굴을 확인했으므로 루프 종료

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        await websocket.close()

@router.post("/search", response_model=dict, summary="특징 벡터로 고객 검색")
async def search_customer(
    feature_vector: list[float],
    threshold: float = 0.7,
    service: CustomerService = Depends(get_customer_service)
) -> dict:
    """
    Milvus 데이터베이스에서 특정 특징 벡터와 유사한 고객을 검색

    - **feature_vector**: 검색할 특징 벡터
    - **threshold**: 유사도 임계값 (0~1 사이)
    - **response**: 유사 고객이 있는 경우 해당 이름, 없으면 메시지
    """
    vector = np.array(feature_vector, dtype=np.float32)
    result = service.search_customer(vector, threshold=threshold)
    if result:
        return {"message": f"Welcome back, {result['name']}!"}
    return {"message": "No matching customer found."}

@router.put("/{customer_id}", response_model=dict, summary="고객 정보 업데이트")
async def update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    service: CustomerService = Depends(get_customer_service)
) -> dict:
    """
    특정 고객의 정보를 업데이트

    - **customer_id**: 업데이트할 고객 ID
    - **customer**: 새로운 고객 정보 (이름과 전화번호 [수정필요])
    - **response**: 성공 메시지
    """
    service.update_customer(customer_id, customer)
    # service.update_customer(customer_id, name, phone_num)
    return {"message": "Customer information updated successfully."}

@router.put("/{customer_id}/update-feature", response_model=dict, summary="특징 벡터 업데이트")
async def update_feature_vector(
    customer_id: int,
    feature_vector: list[float],
    service: CustomerService = Depends(get_customer_service)
) -> dict:
    """
    특정 고객의 특징 벡터를 업데이트

    - **customer_id**: 업데이트할 고객 ID
    - **feature_vector**: 새로운 특징 벡터
    - **response**: 성공 메시지
    """
    vector = np.array(feature_vector, dtype=np.float32)
    service.update_feature_vector(customer_id, vector)
    return {"message": "Feature vector updated successfully."}