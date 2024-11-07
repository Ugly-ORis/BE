from pymilvus import FieldSchema, CollectionSchema, DataType

def get_customer_schema():
    fields = [
        FieldSchema(name="customer_id", dtype=DataType.INT64, is_primary=True, auto_id=True, description="주문자 ID"),
        FieldSchema(name="feature_vector", dtype=DataType.FLOAT_VECTOR, dim=512, description="얼굴 특징 벡터"),
        FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=50, description="이름"),
        FieldSchema(name="phone_last_digits", dtype=DataType.VARCHAR, max_length=4, description="전화번호 뒤 4자리"),
    ]
    return CollectionSchema(fields, description="주문자 정보 컬렉션")
