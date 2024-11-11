from fastapi import APIRouter, HTTPException, Depends
from app.schemas.sale_product_schema import SaleProductCreate, SaleProductUpdate, SaleProductResponse
from app.services.sale_product_service import SaleProductService
from app.api.dependencies import sale_product_client
from typing import List

def get_sale_product_service() -> SaleProductService:
    return SaleProductService(sale_product_client)

router = APIRouter()

# @router.get("/", response_model=List[ToppingResponse])
# async def get_toppings(
#     page: int = Query(1, ge=1),
#     page_size: int = Query(10, ge=1, le=100),
#     service: ToppingService = Depends(get_topping_service)
# ):
#     """
#     페이징된 토핑 목록을 가져오는 API.
#     """
#     offset = (page - 1) * page_size
#     toppings = service.get_toppings(offset=offset, limit=page_size)
    
#     if not toppings:
#         raise HTTPException(status_code=404, detail="No toppings found.")
    
#     return toppings

@router.post("/", response_model=SaleProductResponse)
async def create_sale_product(product: SaleProductCreate, service: SaleProductService = Depends(get_sale_product_service)):
    product_id = service.create_product(product)
    return {**product.dict(), "id": product_id}

@router.get("/{product_id}", response_model=SaleProductResponse)
async def get_sale_product(product_id: int, service: SaleProductService = Depends(get_sale_product_service)):
    product = service.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/{product_id}", response_model=dict)
async def delete_sale_product(product_id: int, service: SaleProductService = Depends(get_sale_product_service)):
    deleted = service.delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found or delete failed")
    return {"message": "Product deleted successfully"}
