from app.schemas.cart_schema import CartCreate, CartResponse
from fastapi import APIRouter, Query, HTTPException, Depends
from app.services.cart_service import CartService
from app.api.dependencies import cart_client
from typing import List
from app.services.cart_service import CartService

    
def get_cart_service() -> CartService:
    return CartService(cart_client)

router = APIRouter()

@router.get("/", response_model=List[CartResponse])

async def get_carts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: CartService = Depends(get_cart_service)
):
    """
    페이징된 장바구니 목록을 가져오는 API.
    """
    offset = (page - 1) * page_size
    carts = service.get_carts(offset=offset, limit=page_size)
    
    if not carts:
        raise HTTPException(status_code=404, detail="No Cart found.")
    
    return carts

@router.post("/", response_model=CartResponse)
async def create_carts(cart: CartCreate, 
                               service: CartService = Depends(get_cart_service)):
    cart_id = service.create_cart(cart)
    return {
        "cart_id": cart_id,
        "customer_id": cart.customer_id,
        "sale_product_id_json": cart.sale_product_id_json,
    }

@router.get("/{cart_id}", response_model=CartResponse)
async def get_cart(cart_id: int, service: CartService = Depends(get_cart_service)):
    cart = service.get_cart(cart_id)
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart

@router.delete("/{cart_id}", response_model=dict)
async def delete_cart(cart_id: int, service: CartService = Depends(get_cart_service)):
    deleted = service.delete_cart(cart_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Cart not found or delete failed")
    return {"message": "Cart deleted successfully"}