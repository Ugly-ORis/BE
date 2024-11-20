from app.db.milvus_client import MilvusClient
from typing import Optional
from app.schemas.sale_product_schema import SaleProductCreate
from app.utils.id_manager import IDManager

class SaleProductService:
    def __init__(self, client: MilvusClient):
        self.client = client
        self.id_manager = IDManager()
        self.id_manager.initialize_default_ids(["Sale_Product"])

    def get_sale_products(self, offset: int, limit: int):
        results = self.client.collection.query(
            expr="", 
            output_fields=["sale_product_id", "ice_cream_id", "topping_id_json", "product_price"], 
            offset=offset, 
            limit=limit
        )
        sale_products = [
            {
                "sale_product_id": result["sale_product_id"],
                "ice_cream_id": result["ice_cream_id"],
                "topping_id_json": result["topping_id_json"],
                "product_price": result["product_price"],
            }
            for result in results
        ]
        return sale_products

    def create_sale_product(self, sale_product: SaleProductCreate) -> int:
        sale_product_id = self.id_manager.get_next_id("Sale_Product")
        entities = [
            [sale_product_id],
            [[0.0, 0.0]],
            [sale_product.ice_cream_id],
            [sale_product.topping_id_json],
            [sale_product.product_price],
        ]
        self.client.collection.insert(entities)
        self.client.collection.flush()
        self.id_manager.update_last_id("Sale_Product", sale_product_id)
        return sale_product_id
    
    def get_sale_product(self, sale_product_id: int) -> Optional[dict]:
        result = self.client.collection.query(
            expr=f"sale_product_id == {sale_product_id}", 
            output_fields=["sale_product_id", "ice_cream_id", "topping_id_json", "product_price"]
        )
        return result[0] if result else None

    def delete_sale_product(self, sale_product_id: int) -> bool:
        return self.client.collection.delete(f"sale_product_id == {sale_product_id}")