from fastapi import APIRouter, Query, HTTPException, Depends
from app.schemas.cart_schema import CartNameResponse
from app.services.cart_service import CartService
from app.api.dependencies import cart_client,ice_cream_client,topping_client
from typing import List
from app.services.cart_service import CartService
from app.services.ice_cream_service import IceCreamService
from app.services.topping_service import ToppingService

    
def get_cart_service() -> CartService:
    return CartService(cart_client)

def get_ice_cream_service() -> IceCreamService:
    return IceCreamService(ice_cream_client)

def get_topping_service() -> ToppingService:
    return ToppingService(topping_client)

router = APIRouter()

@router.get("/", response_model=List[CartNameResponse])  # 여러 개의 카트 정보를 반환
async def get_carts(
    cart_id: List[int] = Query(...),  # 쿼리 매개변수로 카트 ID 리스트 받기
    cart_service: CartService = Depends(get_cart_service), 
    ice_cream_service: IceCreamService = Depends(get_ice_cream_service), 
    topping_service: ToppingService = Depends(get_topping_service)
):
    carts = []  

    for id in cart_id:
        # 각 카트 정보 가져오기
        cart = await cart_service.get_cart_by_id(id)  # 카트 ID로 카트 정보 가져오기
        if cart is None:
            raise HTTPException(status_code=404, detail=f"Cart with ID {id} not found")

        # 아이스크림과 토핑 ID 가져오기
        ice_cream_id = cart.ice_cream_id
        topping_id = cart.topping_id

        # 아이스크림 이름 가져오기
        ice_cream_name_response = ice_cream_service.get_ice_cream_name(ice_cream_id)
        print(ice_cream_name_response)
        # 토핑 이름 가져오기
        topping_name_response = topping_service.get_topping_name(topping_id)

        # CartNameResponse 객체 생성 및 리스트에 추가
        carts.append(CartNameResponse(
            cart_id=cart.cart_id,
            customer_id=cart.customer_id,
            ice_cream_id=cart.ice_cream_id,
            topping_id=cart.topping_id,
            ice_cream_name=ice_cream_name_response,  # 아이스크림 이름
            topping_name=topping_name_response,        # 토핑 이름
            product_price=cart.product_price
        ))

    return carts  # CartNameResponse 리스트 반환
