from app.db.milvus_client import MilvusClient
from app.schemas.topping_schema import ToppingCreate
from typing import Optional
from fastapi import HTTPException


from app.utils.id_manager import IDManager

class ToppingService:
    def __init__(self, client: MilvusClient):
        self.client = client
        self.id_manager = IDManager()
        self.id_manager.initialize_default_ids(["Topping"])

    def get_toppings(self, offset: int, limit: int):
        results = self.client.collection.query(
            expr="", 
            output_fields=["name", "extra_price", "topping_id"], 
            limit=offset + limit 
        )
        
        return results[offset:offset + limit]

    def create_topping(self, topping_data: ToppingCreate) -> int:
        topping_id = self.id_manager.get_next_id("Topping")
        entities = [
            [topping_id],
            [[0.0, 0.0]],
            [topping_data.name],
            [topping_data.extra_price],
            
        ]
        self.client.collection.insert(entities)
        self.client.collection.flush()
        self.id_manager.update_last_id("Topping", topping_id)
        return topping_id

    def get_topping(self, topping_id: int) -> Optional[dict]:
        result = self.client.collection.query(f"topping_id == {topping_id}")
        return result[0] if result else None

    def delete_topping(self, topping_id: int) -> bool:
        delete_result = self.client.collection.delete(f"topping_id == {topping_id}")
        self.client.collection.flush()
        self.client.collection.compact()
        return delete_result is not None

    def get_topping_name(self, topping_id: int) -> Optional[str]:
        result = self.client.collection.query(f"topping_id == {topping_id}",output_fields=["name"])
        
        # 결과가 비어있거나 'name' 키가 없는 경우를 처리
        if not result:
            raise HTTPException(status_code=404, detail="Topping not found")
        
        if 'name' in result[0]:
            return result[0]['name']
        
        raise HTTPException(status_code=404, detail="Topping name not found")