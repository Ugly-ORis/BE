from fastapi import APIRouter, Query, HTTPException, Depends
from app.schemas.order_schema import OrderCreate, OrderResponse
from app.services.order_service import OrderService
from app.api.dependencies import order_client
from typing import List

def get_order_service() -> OrderService:
    return OrderService(order_client)

router = APIRouter()

@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: OrderService = Depends(get_order_service)
):
    """
    페이징된 판매 상품 목록을 가져오는 API.
    """
    offset = (page - 1) * page_size
    orders = service.get_orders(offset=offset, limit=page_size)
    
    if not orders:
        raise HTTPException(status_code=404, detail="No Orders found.")
    
    return orders

@router.post("/", response_model=OrderResponse)
async def create_order(order: OrderCreate, service: OrderService = Depends(get_order_service)):
    order_id = service.create_order(order)
    return {**order.dict(), "order_id": order_id}

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, service: OrderService = Depends(get_order_service)):
    order = service.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.delete("/{order_id}", response_model=dict)
async def delete_order(order_id: int, service: OrderService = Depends(get_order_service)):
    deleted = service.delete_order(order_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Order not found or delete failed")
    return {"message": "Order deleted successfully"}
