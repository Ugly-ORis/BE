from app.db.milvus_client import MilvusClient
from app.schemas.order_schema import OrderCreate, OrderUpdate
from typing import Optional

class OrderService:
    def __init__(self, client: MilvusClient):
        self.client = client

    def create_order(self, order_data: OrderCreate) -> int:
        entities = [
            [order_data.order_datetime],
            [order_data.customer_id],
            [order_data.sale_product_id_json],
            [order_data.total_price]
        ]
        insert_result = self.client.collection.insert(entities)
        self.client.collection.flush()
        return insert_result.primary_keys[0]

    def get_order(self, order_id: int) -> Optional[dict]:
        result = self.client.collection.query(f"order_id == {order_id}")
        return result[0] if result else None

    def update_order(self, order_id: int, order_data: OrderUpdate) -> bool:
        update_fields = {k: v for k, v in order_data.dict().items() if v is not None}
        return self.client.collection.update(order_id, update_fields)

    def delete_order(self, order_id: int) -> bool:
        return self.client.collection.delete(f"order_id == {order_id}")
