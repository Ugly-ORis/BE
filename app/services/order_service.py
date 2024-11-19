from app.db.milvus_client import MilvusClient
from app.schemas.order_schema import OrderCreate, OrderUpdate, OrderResponse
from typing import Optional, List, Dict
from app.utils.id_manager import IDManager

class OrderService:
    def __init__(self, client: MilvusClient):
        self.client = client
        self.id_manager = IDManager()
        self.id_manager.initialize_default_ids(["Order"])

    def get_orders(self, offset: int, limit: int) -> List[Dict]:
        try:
            results = self.client.collection.query(
                expr="order_id >= 0",
                output_fields=["order_id", "order_datetime", "customer_id", "cart_id_json", "total_price", "status"],
                limit=limit,
                offset=offset
            )

            parsed_results = []
            for result in results:
                if isinstance(result, dict):
                    order_dict = {
                        'order_id': result['order_id'],
                        'status': result['status'],
                        'order_datetime': result['order_datetime'],
                        'customer_id': result['customer_id'],
                        'cart_id_json': result['cart_id_json'],  # 딕셔너리로 그대로 유지
                        'total_price': result['total_price']
                    }
                    parsed_results.append(order_dict)

            return parsed_results

        except Exception as e:
            print(f"Error during query: {e}")
            return []  # 오류 발생 시 빈 리스트 반환


    def create_order(self, order_data: OrderCreate) -> int:
        new_order_id = self.id_manager.get_next_id("Order")

        # entities를 주어진 형식으로 정의
        entities = [
            {
                "order_id": new_order_id,
                "customer_id": order_data.customer_id,
                "dummy_vector": [0.1, 0.2],
                "total_price": order_data.total_price,
                "order_datetime": order_data.order_datetime,
                "cart_id_json" : order_data.cart_id_json,
                "status": "Preparing"  # 상태 설정
            }
        ]

        # 데이터 삽입
        insert_result = self.client.collection.insert(entities)
        self.client.collection.flush()

        return new_order_id

    def get_order(self, order_id: int) -> Optional[OrderResponse]:
        try:
            result = self.client.collection.query(f"order_id == {order_id}")
            print("Query result:", result)  # 쿼리 결과 확인

            if result and len(result) > 0:
                return result[0]  # 첫 번째 요소 반환
            return None  # 결과가 없으면 None 반환
        except Exception as e:
            print(f"Error querying order: {e}")
            return None


    def update_order(self, order_id: int, order_data: OrderUpdate) -> bool:
        update_fields = {k: v for k, v in order_data.dict().items() if v is not None}
        return self.client.collection.update(order_id, update_fields)

    def delete_order(self, order_id: int) -> bool:
        return self.client.collection.delete(f"order_id == {order_id}")
