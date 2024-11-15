from app.db.milvus_client import MilvusClient
from app.db.schemas import get_customer_schema, get_order_schema, get_ice_cream_schema, get_topping_schema, get_sale_product_schema, get_id_management_schema
from app.utils.id_manager import IDManager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.api.endpoints import customer, order, ice_cream, topping, sale_product

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "*"]
)

# 엔드포인트 라우터 등록
app.include_router(customer, prefix="/customers", tags=["customers"])
app.include_router(ice_cream, prefix="/ice_cream", tags=["ice_cream"])
app.include_router(topping, prefix="/topping", tags=["topping"])
app.include_router(order, prefix="/order", tags=["order"])
app.include_router(sale_product, prefix="/sale_product", tags=["sale_product"])

@app.on_event("startup")
async def startup_event():
    print("Starting up and initializing Milvus collections...")

    MilvusClient("Customer", get_customer_schema(), vector_index_field="image_vector", numeric_index_field="customer_id")
    MilvusClient("Order", get_order_schema(), numeric_index_field="order_id")
    MilvusClient("Ice_cream", get_ice_cream_schema(), numeric_index_field="ice_cream_id")
    MilvusClient("Topping", get_topping_schema(), numeric_index_field="topping_id")
    MilvusClient("Sale_product", get_sale_product_schema(), numeric_index_field="sale_product_id")
    MilvusClient("ID_Management", get_id_management_schema())

    id_manager = IDManager()
    id_manager.initialize_default_ids(["Customer", "Order", "Sale_Product", "Ice_Cream", "Topping"])
    print("All collections initialized and loaded successfully.")
