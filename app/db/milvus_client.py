from typing import Optional
from pymilvus import connections, Collection, utility, MilvusException

class MilvusClient:
    def __init__(self, collection_name: str, schema, vector_index_field: str = "dummy_vector", numeric_index_field: Optional[str] = None):
        self.collection_name = collection_name
        self.vector_index_field = vector_index_field
        self.numeric_index_field = numeric_index_field

        connections.connect("default", host="localhost", port="19530")
        self.collection = self.get_or_create_collection(schema)
        self.create_vector_index(self.vector_index_field)
        
        if self.numeric_index_field:
            self.create_numeric_index(self.numeric_index_field)

        self.load_collection()

    def get_or_create_collection(self, schema):
        """컬렉션을 가져오거나 생성"""
        if not utility.has_collection(self.collection_name):
            print(f"Creating collection '{self.collection_name}'.")
            return Collection(name=self.collection_name, schema=schema)
        print(f"Loading existing collection '{self.collection_name}'.")
        return Collection(name=self.collection_name)

    def create_vector_index(self, field_name: str):
        """벡터 필드에 대한 인덱스 생성"""
        nlist_value = 128 if field_name == "feature_vector" else 1
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": nlist_value}
        }
        try:
            self.collection.create_index(field_name=field_name, index_params=index_params)
            print(f"Vector index created for field '{field_name}' with nlist set to {nlist_value}.")
        except MilvusException as e:
            print(f"Error creating vector index for field '{field_name}': {e}")

    def create_numeric_index(self, field_name: str):
        """숫자 필드에 대한 인덱스를 생성"""
        index_name = f"{field_name}_idx"
        try:
            self.collection.create_index(field_name=field_name, index_name=index_name)
            print(f"Numeric index created for field '{field_name}' with name '{index_name}'.")
        except MilvusException as e:
            print(f"Error creating numeric index for field '{field_name}': {e}")

    def load_collection(self):
        """컬렉션 로드 시도 및 에러 처리"""
        try:
            self.collection.load()
            print(f"Collection '{self.collection_name}' loaded successfully.")
        except MilvusException as e:
            if 'index not found' in str(e):
                print(f"Warning: No index found for '{self.collection_name}', but collection loaded without an index.")
            else:
                raise e
