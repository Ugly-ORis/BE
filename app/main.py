from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.api.endpoints.customer import customer
from app.api.endpoints.order import order
from app.api.endpoints.ice_cream import ice_cream
from app.api.endpoints.topping import topping
from app.api.endpoints.sale_product import sale_product

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
app.include_router(customer.router, prefix="/customers", tags=["customers"])
app.include_router(ice_cream.router, prefix="/ice_cream", tags=["ice_cream"])
app.include_router(topping.router, prefix="/topping", tags=["topping"])
app.include_router(order.router, prefix="/order", tags=["order"])
app.include_router(sale_product.router, prefix="/sale_product", tags=["sale_product"])
