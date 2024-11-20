from pymilvus import FieldSchema, CollectionSchema, DataType

def get_cart_schema():
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True, description="Primary Key ID"),
        FieldSchema(name="cart_id", dtype=DataType.INT64, description="cart ID"),
        FieldSchema(name="customer_id", dtype=DataType.INT64, description="소비자 ID"),
        FieldSchema(name="dummy_vector", dtype=DataType.FLOAT_VECTOR, dim=2, description="더미 벡터"),
        FieldSchema(name="sale_product_id_json", dtype=DataType.JSON, description="판매상품 ID JSON"),
    ]
    return CollectionSchema(fields, description="장바구니 정보 컬렉션")
