from app.db.milvus_client import MilvusClient
from app.schemas.topping import ToppingCreate, ToppingUpdate
from typing import Optional

class ToppingService:
    def __init__(self, client: MilvusClient):
        self.client = client

    def create_topping(self, topping_data: ToppingCreate) -> int:
        entities = [
            [topping_data.name],
            [topping_data.price],
            [topping_data.availability]
        ]
        insert_result = self.client.collection.insert(entities)
        self.client.collection.flush()
        return insert_result.primary_keys[0]

    def get_topping(self, topping_id: int) -> Optional[dict]:
        result = self.client.collection.query(f"id == {topping_id}")
        return result[0] if result else None

    def update_topping(self, topping_id: int, topping_data: ToppingUpdate) -> bool:
        update_fields = {k: v for k, v in topping_data.dict().items() if v is not None}
        return self.client.collection.update(topping_id, update_fields)

    def delete_topping(self, topping_id: int) -> bool:
        return self.client.collection.delete(f"id == {topping_id}")
