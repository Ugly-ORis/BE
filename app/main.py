from fastapi import FastAPI
from app.api.endpoints import customer

app = FastAPI()

# 엔드포인트 라우터 등록
app.include_router(customer.router, prefix="/customers", tags=["customers"])
