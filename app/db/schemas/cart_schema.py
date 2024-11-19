from pymilvus import FieldSchema, CollectionSchema, DataType

def get_cart_schema():
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True, description="Primary Key ID"),
        FieldSchema(name="cart_id", dtype=DataType.INT64, description="cart ID"),
        FieldSchema(name="customer_id", dtype=DataType.INT64, description="소비자 ID"),
        FieldSchema(name="dummy_vector", dtype=DataType.FLOAT_VECTOR, dim=2, description="더미 벡터"),
        FieldSchema(name="ice_cream_id", dtype=DataType.INT64, description="아이스크림 ID"),
        FieldSchema(name="topping_id", dtype=DataType.INT64, description="토핑 ID"),
        FieldSchema(name="product_price", dtype=DataType.INT64, description="판매 가격"),
    ]
    return CollectionSchema(fields, description="판매 상품 정보 컬렉션")
