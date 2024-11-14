from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.api.endpoints import customer, order, ice_cream, topping, sale_product, robot_topcam_view

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
    TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "*"] ## CORS = 접속 할 IP  * = 전체 접속
)

# 엔드포인트 라우터 등록
app.include_router(customer, prefix="/customers", tags=["customers"])
app.include_router(ice_cream, prefix="/ice_cream", tags=["ice_cream"])
app.include_router(topping, prefix="/topping", tags=["topping"])
app.include_router(order, prefix="/order", tags=["order"])
app.include_router(sale_product, prefix="/sale_product", tags=["sale_product"])
app.include_router(robot_topcam_view, prefix="/robot_topcam_view", tags=["robot_topcam_view"])
