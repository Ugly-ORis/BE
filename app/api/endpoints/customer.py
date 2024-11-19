import numpy as np
from typing import List

from fastapi import Query, APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.customer_schema import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services.customer_service import CustomerService
from app.api.dependencies import customer_client

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

@router.get("/video", response_model=None)
def video_stream(
    service: CustomerService = Depends(get_customer_service)
):
    return StreamingResponse(service.track_and_get_feature(), 
                             media_type="multipart/x-mixed-replace; boundary=frame")

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
