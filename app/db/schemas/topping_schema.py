from pymilvus import FieldSchema, CollectionSchema, DataType, Collection

def get_topping_schema():
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True, description="Primary Key ID"),
        FieldSchema(name="topping_id", dtype=DataType.INT64, description="토핑 ID"),
        FieldSchema(name="dummy_vector", dtype=DataType.FLOAT_VECTOR, dim=2, description="더미 벡터"),
        FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=20, description="토핑 이름"),
        FieldSchema(name="extra_price", dtype=DataType.FLOAT, description="토핑 추가 가격"),
        FieldSchema(name="image", dtype=DataType.VARCHAR, max_length=65535, description="토핑 이미지")
    ]
    return CollectionSchema(fields, description="토핑 정보 컬렉션")
