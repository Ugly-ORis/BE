import base64
from app.db.milvus_client import MilvusClient
from app.schemas.ice_cream_schema import IceCreamCreate
from typing import Optional
from PIL import Image
from io import BytesIO

from app.utils.id_manager import IDManager
from app.utils.vector_converter import VectorConverter

class IceCreamService:
    def __init__(self, client: MilvusClient):
        self.client = client
        self.id_manager = IDManager()
        self.id_manager.initialize_default_ids(["Ice_Cream"])
        self.converter = VectorConverter()

    def get_ice_creams(self, offset: int, limit: int):
        results = self.client.collection.query(
            expr="", 
            output_fields=["ice_cream_id", "name", "flavor", "price", "image"], 
            offset=offset, 
            limit=limit
        )
        ice_creams = [
            {
                "ice_cream_id": result["ice_cream_id"],
                "name": result["name"],
                "flavor": result["flavor"],
                "price": result["price"],
                "image": result["image"]
            }
            for result in results
        ]
        return ice_creams

    def create_ice_cream(self, ice_cream: IceCreamCreate, pil_image) -> int:
        image = self.resize_and_convert_to_base64(pil_image)
        ice_cream_id = self.id_manager.get_next_id("Ice_Cream")
        entities = [
            [ice_cream_id],
            [[0.0, 0.0]],
            [ice_cream.name],
            [ice_cream.flavor],
            [ice_cream.price],
            [image]
        ]
        self.client.collection.insert(entities)
        self.client.collection.flush()
        self.id_manager.update_last_id("Ice_Cream", ice_cream_id)
        return ice_cream_id
    
    def get_ice_cream(self, ice_cream_id: int) -> Optional[dict]:
        result = self.client.collection.query(
            expr=f"ice_cream_id == {ice_cream_id}", 
            output_fields=["ice_cream_id", "name", "flavor", "price"]
        )
        return result[0] if result else None


    def delete_ice_cream(self, ice_cream_id: int) -> bool:
        return self.client.collection.delete(f"ice_cream_id == {ice_cream_id}")

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


