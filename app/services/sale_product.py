from app.api.endpoints.ice_cream import get_ice_cream_service
from app.api.endpoints.topping import get_topping_service
from app.db.milvus_client import MilvusClient
from typing import Optional
from app.schemas.sale_product_schema import SaleProductCreate
from app.services.ice_cream_service import IceCreamService
from app.services.topping_service import ToppingService
from app.utils.id_manager import IDManager
from typing import Optional, Dict, List

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
    
    def get_sale_product(self, sale_product_id: int) -> Optional[Dict]:
        if not (result := self.client.collection.query(
            expr=f"sale_product_id == {sale_product_id}",
            output_fields=["sale_product_id", "ice_cream_id", "topping_id_json", "product_price"]
        )):
            return None

        sale_product = result[0]
        topping_ids: List[int] = sale_product.get("topping_id_json", [])

        topping_data = []
        if topping_ids:
            topping_service: ToppingService = get_topping_service()
            for topping_id in topping_ids:
                topping = topping_service.get_topping(topping_id)
                if topping:
                    topping_data.append(topping)

        ice_cream_service: IceCreamService = get_ice_cream_service()
        ice_cream = ice_cream_service.get_ice_cream(sale_product["ice_cream_id"])
        ice_cream_name = ice_cream["name"] if ice_cream else None

        sale_product["topping_data"] = topping_data  
        sale_product["ice_cream_name"] = ice_cream_name 

        return sale_product

    def delete_sale_product(self, sale_product_id: int) -> bool:
        return self.client.collection.delete(f"sale_product_id == {sale_product_id}")