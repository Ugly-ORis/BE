from pymilvus import FieldSchema, CollectionSchema, DataType

def get_id_management_schema():
    fields = [
        FieldSchema(name="collection_name", dtype=DataType.VARCHAR, max_length=50, is_primary=True),
        FieldSchema(name="dummy_vector", dtype=DataType.FLOAT_VECTOR, dim=2, description="더미 벡터"),
        FieldSchema(name="last_id", dtype=DataType.INT64, description="마지막 ID 값") 
    ]
    return CollectionSchema(fields, description="ID 관리용 컬렉션")
