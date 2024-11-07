from pymilvus import FieldSchema, CollectionSchema, DataType

def get_order_schema():
    fields = [
        FieldSchema(name="order_id", dtype=DataType.INT64, is_primary=True, auto_id=True, description="주문 ID"),
        FieldSchema(name="dummy_vector", dtype=DataType.FLOAT_VECTOR, dim=2, description="더미 벡터"),
        FieldSchema(name="order_datetime", dtype=DataType.VARCHAR, max_length=50, description="주문 날짜, 시간"),
        FieldSchema(name="customer_id", dtype=DataType.INT64, description="주문자 ID"),
        FieldSchema(name="sale_product_id_json", dtype=DataType.JSON, description="판매 상품 ID JSON"),
        FieldSchema(name="total_price", dtype=DataType.FLOAT, description="총 주문 금액"),
    ]
    return CollectionSchema(fields, description="주문 정보 컬렉션")
