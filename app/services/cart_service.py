from app.db.milvus_client import MilvusClient
from app.schemas.cart_schema import CartCreate, CartUpdate, CartResponse
from typing import Optional, List, Dict

class CartService:
    def __init__(self, client: MilvusClient):
        self.client = client

    # ... (다른 메서드 생략)

    async def get_cart_by_id(self, cart_id: int) -> Optional[CartResponse]:
        """특정 카트 ID에 대한 CartResponse를 반환합니다."""
        product = await self.get_product(cart_id)  
        if product:
            return CartResponse(
                cart_id=product['cart_id'],
                ice_cream_id=product['ice_cream_id'],
                customer_id=product['customer_id'],
                topping_id=product['topping_id'],
                product_price=product['product_price']
            )
        return None  # 제품을 찾지 못한 경우 None 반환

    async def get_product(self, product_id: int) -> Optional[dict]:
        # cart_id로 쿼리 수정
        result = self.client.collection.query(f"cart_id == {product_id}", output_fields=["cart_id", "ice_cream_id", "customer_id", "topping_id", "product_price"])
        
        # 결과가 비어 있지 않으면 첫 번째 요소를 반환
        return result[0] if result else None
    

    async def delete_carts(self, cart_ids: List[int]) -> None:
        for cart_id in cart_ids:
            # cart_id에 해당하는 항목 삭제
            self.client.collection.delete({"cart_id": cart_id})
