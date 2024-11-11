from pymilvus import FieldSchema, CollectionSchema, DataType

def get_sale_product_schema():
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True, description="Primary Key ID"),
        FieldSchema(name="sale_product_id", dtype=DataType.INT64, description="판매 상품 ID"),
        FieldSchema(name="dummy_vector", dtype=DataType.FLOAT_VECTOR, dim=2, description="더미 벡터"),
        FieldSchema(name="ice_cream_id", dtype=DataType.INT64, description="아이스크림 ID"),
        FieldSchema(name="topping_id_json", dtype=DataType.JSON, description="토핑 ID JSON"),
        FieldSchema(name="product_price", dtype=DataType.FLOAT, description="판매 가격"),
    ]
    return CollectionSchema(fields, description="판매 상품 정보 컬렉션")
