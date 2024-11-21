import base64
from app.db.milvus_client import MilvusClient
from app.schemas.topping_schema import ToppingCreate
from typing import Optional
from PIL import Image
from io import BytesIO


from app.utils.id_manager import IDManager

class ToppingService:
    def __init__(self, client: MilvusClient):
        self.client = client
        self.id_manager = IDManager()
        self.id_manager.initialize_default_ids(["Topping"])

    def get_toppings(self, offset: int, limit: int):
        results = self.client.collection.query(
            expr="", 
            output_fields=["name", "extra_price", "topping_id", "image"], 
            limit=offset + limit 
        )
        toppings = [
            {
                "topping_id": result["topping_id"],
                "name": result["name"],
                "extra_price": result["extra_price"],
                "image": result["image"]
            }
            for result in results
        ]
        
        return toppings
    
    def create_topping(self, topping_data: ToppingCreate, pil_image) -> int:
        image = self.resize_and_convert_to_base64(pil_image)
        topping_id = self.id_manager.get_next_id("Topping")
        entities = [
            [topping_id],
            [[0.0, 0.0]],
            [topping_data.name],
            [topping_data.extra_price],
            [image]
        ]
        self.client.collection.insert(entities)
        self.client.collection.flush()
        self.id_manager.update_last_id("Topping", topping_id)
        return topping_id

    def get_topping(self, topping_id: int) -> Optional[dict]:
        result = self.client.collection.query(
            expr=f"topping_id == {topping_id}", 
            output_fields=["topping_id", "name", "extra_price"]
        )
        return result[0] if result else None

    def delete_topping(self, topping_id: int) -> bool:
        delete_result = self.client.collection.delete(f"topping_id == {topping_id}")
        self.client.collection.flush()
        self.client.collection.compact()
        return delete_result is not None

    def resize_and_convert_to_base64(self, pil_image, max_size_bytes=65535) -> str:
        buffer = BytesIO()
        quality = 85 

        pil_image.save(buffer, format="JPEG", quality=quality)

        while True:
            base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
            if len(base64_image) <= max_size_bytes:
                break  

            quality -= 5
            if quality < 10:  
                width, height = pil_image.size
                pil_image = pil_image.resize((width // 2, height // 2))
                quality = 85 

            buffer = BytesIO()
            pil_image.save(buffer, format="JPEG", quality=quality)

        return base64_image