from app.db.milvus_client import MilvusClient
from app.schemas.sale_product import SaleProductCreate, SaleProductUpdate
from typing import Optional

class SaleProductService:
    def __init__(self, client: MilvusClient):
        self.client = client

    def create_product(self, product_data: SaleProductCreate) -> int:
        entities = [
            [product_data.ice_cream_id],
            [product_data.topping_id_json],
            [product_data.product_price]
        ]
        insert_result = self.client.collection.insert(entities)
        self.client.collection.flush()
        return insert_result.primary_keys[0]

    def get_product(self, product_id: int) -> Optional[dict]:
        result = self.client.collection.query(f"id == {product_id}")
        return result[0] if result else None

    def update_product(self, product_id: int, product_data: SaleProductUpdate) -> bool:
        update_fields = {k: v for k, v in product_data.dict().items() if v is not None}
        return self.client.collection.update(product_id, update_fields)

    def delete_product(self, product_id: int) -> bool:
        return self.client.collection.delete(f"id == {product_id}")
