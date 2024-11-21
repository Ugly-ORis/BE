from app.api.endpoints.sale_product import get_sale_product_service
from app.db.milvus_client import MilvusClient
from typing import Dict, Optional
from app.schemas.cart_schema import CartCreate, CartResponse
from app.services.sale_product import SaleProductService
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
    
    def get_cart(self, cart_id: int) -> Optional[Dict]:
        if not (result := self.client.collection.query(
            expr=f"cart_id == {cart_id}", 
            output_fields=["cart_id", "customer_id", "sale_product_id_json"]
        )):
            return None

        cart = result[0]

        sale_product_service: SaleProductService = get_sale_product_service()

        sale_products = []
        for sale_product_id in cart["sale_product_id_json"]:
            sale_product = sale_product_service.get_sale_product(sale_product_id)
            if sale_product:
                sale_products.append(sale_product)

        return CartResponse(
            cart_id=cart["cart_id"],
            customer_id=cart["customer_id"],
            sale_product_id_json=cart["sale_product_id_json"],
            sale_products=sale_products
        )

    def delete_cart(self, cart_id: int) -> bool:
        return self.client.collection.delete(f"cart_id == {cart_id}")