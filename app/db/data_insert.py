from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType

connections.connect("default", host="localhost", port="19530")

# # Ice Cream 더미 데이터
# ice_cream_data = [
#     {"ice_cream_id": 1, "dummy_vector": [0.1, 0.2], "name": "Vanilla", "flavor": "Classic vanilla flavor", "price": 300},
#     {"ice_cream_id": 2, "dummy_vector": [0.3, 0.4], "name": "Chocolate", "flavor": "Rich chocolate flavor", "price": 350},
#     {"ice_cream_id": 3, "dummy_vector": [0.5, 0.6], "name": "Strawberry", "flavor": "Fresh strawberry flavor", "price": 320},
# ]

# ice_cream_collection = Collection("Ice_cream")
# ice_cream_collection.insert(ice_cream_data)

# # Topping 더미 데이터
# topping_data = [
#     {"topping_id": 1, "dummy_vector": [0.1, 0.2], "name": "Chocolate Chips", "extra_price": 50},
#     {"topping_id": 2, "dummy_vector": [0.3, 0.4], "name": "Sprinkles", "extra_price": 30},
#     {"topping_id": 3, "dummy_vector": [0.5, 0.6], "name": "Nuts", "extra_price": 40},
# ]

# topping_collection = Collection("Topping")
# topping_collection.insert(topping_data)

# Cart 더미 데이터
# cart_data = [
#     {"cart_id":1, "customer_id": 1, "dummy_vector": [0.1, 0.2], "ice_cream_id": 1, "topping_id": 1, "product_price": 350},
#     {"cart_id":2, "customer_id": 1, "dummy_vector": [0.3, 0.4], "ice_cream_id": 2, "topping_id": 2, "product_price": 380},
#     {"cart_id":3,"customer_id": 2, "dummy_vector": [0.5, 0.6], "ice_cream_id": 3, "topping_id": 3, "product_price": 360},
# ]

# cart_collection = Collection("Cart")
# cart_collection.insert(cart_data)


# ID_Management 더미 데이터
id_data = [
    {"collection_name":"Order", "dummy_vector": [0.1, 0.2], "last_id": 1}
]

id_collection = Collection("ID_Management")
id_collection.insert(id_data)

# # Order 더미 데이터
# order_data = [
#     {
#         "order_id": 1, 
#         "dummy_vector": [0.1, 0.2], 
#         "order_datetime": "2023-11-18 12:00:00", 
#         "customer_id": 1, 
#         "cart_id_json": [1, 2],  # Cart ID 리스트
#         "total_price": 730,  # 예시 총 가격
#         "status": "Preparing"
#     },
#     {
#         "order_id": 2, 
#         "dummy_vector": [0.3, 0.4], 
#         "order_datetime": "2023-11-18 12:30:00", 
#         "customer_id": 2, 
#         "cart_id_json": [3],  # Cart ID 리스트
#         "total_price": 360,  # 예시 총 가격
#         "status": "Serving"
#     },
# ]

# order_collection = Collection("Order")
# order_collection.insert(order_data)
