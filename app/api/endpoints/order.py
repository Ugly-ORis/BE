from fastapi import APIRouter, HTTPException, Depends
from app.schemas.order_schema import OrderCreate, OrderUpdate, OrderResponse
from app.services.order_service import OrderService
from app.api.dependencies import order_client
from typing import List

def get_order_service() -> OrderService:
    return OrderService(order_client)

router = APIRouter()

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

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(order_id: int, order: OrderUpdate, service: OrderService = Depends(get_order_service)):
    updated = service.update_order(order_id, order)
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found or update failed")
    return {**order.dict(exclude_unset=True), "order_id": order_id}

@router.delete("/{order_id}", response_model=dict)
async def delete_order(order_id: int, service: OrderService = Depends(get_order_service)):
    deleted = service.delete_order(order_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Order not found or delete failed")
    return {"message": "Order deleted successfully"}
