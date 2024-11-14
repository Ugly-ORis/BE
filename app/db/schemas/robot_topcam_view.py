from pymilvus import FieldSchema, CollectionSchema, DataType

def get_topcam_schema():
    fields = [
        FieldSchema(name="aruco_marker_id", dtype=DataType.INT64, is_primary=True, auto_id=True, description="marker_id"),
        # FieldSchema(name="dummy_vector", dtype=DataType.FLOAT_VECTOR, dim=2, description="더미 벡터"),
        # FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=50, description="아이스크림 이름"),
        # FieldSchema(name="flavor", dtype=DataType.VARCHAR, max_length=200, description="맛(설명)"),
        # FieldSchema(name="price", dtype=DataType.FLOAT, description="기본 가격"),
    ]
    return CollectionSchema(fields, description="아리스 상단 캠 정보 컬렉션")
