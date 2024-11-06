from pymilvus import connections, Collection, utility, FieldSchema, CollectionSchema, DataType, Index

class MilvusClient:
    def __init__(self, collection_name="Customer"):
        self.collection_name = collection_name
        connections.connect("default", host="localhost", port="19530")
        self.collection = self.get_or_create_collection()
        self.create_index()

    def get_or_create_collection(self):
        fields = [
            FieldSchema(name="customer_id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="feature_vector", dtype=DataType.FLOAT_VECTOR, dim=512),
            FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="phone_last_digits", dtype=DataType.VARCHAR, max_length=4),
        ]
        schema = CollectionSchema(fields, description="Customer data")

        if not utility.has_collection(self.collection_name):
            collection = Collection(name=self.collection_name, schema=schema)
            print(f"Collection '{self.collection_name}' created.")
        else:
            collection = Collection(name=self.collection_name)
            print(f"Collection '{self.collection_name}' loaded.")
        
        return collection

    def create_index(self):
        index_params = {
            "metric_type": "L2",  # L2 또는 IP (Inner Product) 사용 가능
            "index_type": "IVF_FLAT",  # Milvus에서 사용할 인덱스 유형
            "params": {"nlist": 128}   # 클러스터 수 지정
        }

        # feature_vector 필드에 인덱스 생성
        if not self.collection.has_index():
            self.collection.create_index(field_name="feature_vector", index_params=index_params)
            print("Index created for feature_vector.")
        else:
            print("Index already exists.")