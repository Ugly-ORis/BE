from fastapi import APIRouter, Depends, HTTPException
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.customer_service import CustomerService
from app.db.milvus_client import MilvusClient
import numpy as np

router = APIRouter()

def get_customer_service() -> CustomerService:
    milvus_client = MilvusClient()
    return CustomerService(milvus_client)

@router.post("/customers", response_model=dict, summary="새 고객 추가")
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

@router.post("/customers/capture", response_model=dict)
async def capture_face(service: CustomerService = Depends(get_customer_service)):
    """
    카메라에서 얼굴을 추적하고 선택한 얼굴의 특징 벡터를 추출하여 DB에 저장하거나 기존 고객을 검색합니다.
    """
    try:
        feature_vector = service.track_and_get_feature()
        if feature_vector is None:
            return {"message": "Face not detected or not selected."}

        result = service.search_customer(feature_vector)
        if result.get("name"):
            return {"message": f"Welcome back, {result['name']}!"}

        customer_id = service.insert_customer(feature_vector, "New User", "0000")
        return {"message": "New user created.", "customer_id": customer_id}

    except Exception as e:
        return {"error": str(e), "message": "An error occurred during face capture"}

@router.post("/customers/search", response_model=dict, summary="특징 벡터로 고객 검색")
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

@router.put("/customers/{customer_id}", response_model=dict, summary="고객 정보 업데이트")
async def update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    service: CustomerService = Depends(get_customer_service)
) -> dict:
    """
    특정 고객의 정보를 업데이트

    - **customer_id**: 업데이트할 고객 ID
    - **customer**: 새로운 고객 정보
    - **response**: 성공 메시지
    """
    service.update_customer(customer_id, customer)
    return {"message": "Customer information updated successfully."}

@router.put("/customers/{customer_id}/update-feature", response_model=dict, summary="특징 벡터 업데이트")
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
