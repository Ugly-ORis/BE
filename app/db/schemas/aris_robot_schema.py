from pymilvus import FieldSchema, CollectionSchema, DataType

def aris_robot_schema():
    fields = [
        FieldSchema(name="robot_id", dtype=DataType.INT64, is_primary=True, auto_id=True, description="로봇 ID"),
    ]
    return CollectionSchema(fields, description="로봇 정보 컬렉션")
