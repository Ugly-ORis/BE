from fastapi import APIRouter, Query, HTTPException, Depends,FastAPI
from app.schemas.order_schema import OrderCreate, OrderResponse

from app.services.order_service import OrderService
from app.services.cart_service import CartService


from app.api.dependencies import order_client, cart_client
from typing import List,Dict
from fastapi.middleware.cors import CORSMiddleware

def get_order_service() -> OrderService:
    return OrderService(order_client)

def get_cart_service() -> CartService:
    return CartService(cart_client)

router = APIRouter()

def get_order_service() -> OrderService:
    return OrderService(order_client)

@router.post("/", response_model=dict)
async def create_order(order: OrderCreate, 
    service: OrderService = Depends(get_order_service),
    cart_service : CartService  = Depends(get_cart_service)) -> int:
    
    order_id = service.create_order(order)  # OrderService의 create_order 호출
    cart_service.delete_carts(order.cart_id_json)
    return {"order_id":order_id}  # 생성된 order_id 반환

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

@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    service: OrderService = Depends(get_order_service)
):
    offset = (page - 1) * pageSize
    try:
        # 서비스에서 주문 목록을 가져옴
        orders = service.get_orders(offset=offset, limit=pageSize)

        parsed_orders = []
        for order in orders:
            order_response = OrderResponse(
                order_id=order['order_id'],
                status=order['status'],
                order_datetime=order['order_datetime'],
                customer_id=order['customer_id'],
                cart_id_json=order['cart_id_json'], 
                total_price=order['total_price']
            )
            parsed_orders.append(order_response)

        # 주문이 없을 경우 빈 리스트를 반환
        return parsed_orders  # parsed_orders가 비어있으면 빈 리스트가 반환됨

    except Exception as e:
        print(f"Error retrieving orders: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    