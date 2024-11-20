from app.db.milvus_client import MilvusClient
from app.schemas.order_schema import OrderCreate
from typing import Optional, List, Dict
from app.utils.id_manager import IDManager

class OrderService:
    def __init__(self, client: MilvusClient):
        self.client = client
        self.id_manager = IDManager()
        self.id_manager.initialize_default_ids(["Order"])

    def get_orders(self, offset: int, limit: int):
        results = self.client.collection.query(
            expr="", 
            output_fields=["order_id", "order_datetime", "customer_id", "cart_id", "total_price", "status"], 
            offset=offset, 
            limit=limit
        )
        orders = [
            {
                "order_id": result["order_id"],
                "order_datetime": result["order_datetime"],
                "customer_id": result["customer_id"],
                "cart_id": result["cart_id"],
                "total_price": result["total_price"],
                "status": result["status"],
            }
            for result in results
        ]
        return orders

    def create_order(self, order: OrderCreate) -> int:
        order_id = self.id_manager.get_next_id("Order")
        entities = [
            [order_id],
            [[0.0, 0.0]],
            [order.order_datetime],
            [order.customer_id],
            [order.cart_id],
            [order.total_price],
            [order.status],
        ]
        self.client.collection.insert(entities)
        self.client.collection.flush()
        self.id_manager.update_last_id("Order", order_id)
        return order_id
    
    def get_order(self, order_id: int) -> Optional[dict]:
        result = self.client.collection.query(
            expr=f"order_id == {order_id}", 
            output_fields=["order_id", "order_datetime", "customer_id", "cart_id", "total_price", "status"]
        )
        return result[0] if result else None

    def delete_order(self, order_id: int) -> bool:
        return self.client.collection.delete(f"order_id == {order_id}")