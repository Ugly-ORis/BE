from app.schemas.sale_product_schema import SaleProductCreate, SaleProductResponse
from app.services.sale_product import SaleProductService
from fastapi import APIRouter, Query, HTTPException, Depends
from app.services.ice_cream_service import IceCreamService
from app.api.dependencies import  sale_product_client
from typing import List

def get_sale_product_service() -> SaleProductService:
    return SaleProductService(sale_product_client)

router = APIRouter()

@router.get("/", response_model=List[SaleProductResponse])
async def get_sale_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: SaleProductService = Depends(get_sale_product_service)
):
    """
    페이징된 판매 상품 목록을 가져오는 API.
    """
    offset = (page - 1) * page_size
    sale_products = service.get_sale_products(offset=offset, limit=page_size)
    
    if not sale_products:
        raise HTTPException(status_code=404, detail="No Sale-Product found.")
    
    return sale_products

@router.post("/", response_model=SaleProductResponse)
async def create_sale_products(sale_product: SaleProductCreate, 
                               service: SaleProductService = Depends(get_sale_product_service)):
    sale_product_id = service.create_sale_product(sale_product)
    return {
        "sale_product_id": sale_product_id,
        "ice_cream_id": sale_product.ice_cream_id,
        "topping_id_json": sale_product.topping_id_json,
        "product_price": sale_product.product_price
    }

@router.get("/{sale_product_id}", response_model=SaleProductResponse)
async def get_sale_product(sale_product_id: int, service: SaleProductService = Depends(get_sale_product_service)):
    sale_product = service.get_sale_product(sale_product_id)
    if sale_product is None:
        raise HTTPException(status_code=404, detail="Sale-Product not found")
    return sale_product

@router.delete("/{sale_product_id}", response_model=dict)
async def delete_sale_product(sale_product_id: int, service: SaleProductService = Depends(get_sale_product_service)):
    deleted = service.delete_sale_product(sale_product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sale-Product not found or delete failed")
    return {"message": "Sale-Product deleted successfully"}
