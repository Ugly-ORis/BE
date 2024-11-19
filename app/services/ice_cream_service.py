from app.db.milvus_client import MilvusClient
from app.schemas.ice_cream_schema import IceCreamCreate, IceCreamUpdate
from typing import Optional
from fastapi import HTTPException

class IceCreamService:
    def __init__(self, client: MilvusClient):
        self.client = client

    def get_ice_creams(self, offset: int, limit: int):
        results = self.client.collection.query(
            expr="", 
            output_fields=["ice_cream_id", "name", "flavor", "price"], 
            limit=offset + limit 
        )
        
        return results[offset:offset + limit]

    def create_ice_cream(self, ice_cream_data: IceCreamCreate) -> int:
        entities = [
            [ice_cream_data.name],
            [ice_cream_data.flavor],
            [ice_cream_data.price],
            [ice_cream_data.stock]
        ]
        insert_result = self.client.collection.insert(entities)
        self.client.collection.flush()
        return insert_result.primary_keys[0]

    def get_ice_cream(self, ice_cream_id: int) -> Optional[dict]:
        result = self.client.collection.query(f"id == {ice_cream_id}")
        return result[0] if result else None

    def update_ice_cream(self, ice_cream_id: int, ice_cream_data: IceCreamUpdate) -> bool:
        update_fields = {k: v for k, v in ice_cream_data.dict().items() if v is not None}
        return self.client.collection.update(ice_cream_id, update_fields)

    def delete_ice_cream(self, ice_cream_id: int) -> bool:
        return self.client.collection.delete(f"id == {ice_cream_id}")
    
    def get_ice_cream_name(self, ice_cream_id: int) -> Optional[str]:
        result = self.client.collection.query(f"ice_cream_id == {ice_cream_id}",output_fields=["name"])
        
        # 결과가 비어있는 경우 처리
        if not result:
            raise HTTPException(status_code=404, detail="Ice cream not found")
        
        # 'name' 키가 있는지 확인
        if 'name' in result[0]:
            return result[0]['name']
        
        raise HTTPException(status_code=404, detail="Ice cream name not found")