from app.db.milvus_client import MilvusClient
from typing import Optional

from app.schemas.cart_schema import CartCreate
from app.utils.id_manager import IDManager

class CartService:
    def __init__(self, client: MilvusClient):
        self.client = client
        self.id_manager = IDManager()
        self.id_manager.initialize_default_ids(["Cart"])

    def get_carts(self, offset: int, limit: int):
        results = self.client.collection.query(
            expr="", 
            output_fields=["cart_id", "customer_id", "sale_product_id_json"], 
            offset=offset, 
            limit=limit
        )
        carts = [
            {
                "cart_id": result["cart_id"],
                "customer_id": result["customer_id"],
                "sale_product_id_json": result["sale_product_id_json"],
            }
            for result in results
        ]
        return carts

    def create_cart(self, cart: CartCreate) -> int:
        cart_id = self.id_manager.get_next_id("Cart")
        entities = [
            [cart_id],
            [cart.customer_id],
            [[0.0, 0.0]],
            [cart.sale_product_id_json],
        ]
        self.client.collection.insert(entities)
        self.client.collection.flush()
        self.id_manager.update_last_id("Cart", cart_id)
        return cart_id
    
    def get_cart(self, cart_id: int) -> Optional[dict]:
        result = self.client.collection.query(
            expr=f"cart_id == {cart_id}", 
            output_fields=["cart_id", "customer_id", "sale_product_id_json"]
        )
        return result[0] if result else None

    def delete_cart(self, cart_id: int) -> bool:
        return self.client.collection.delete(f"cart_id == {cart_id}")