from fastapi import APIRouter, HTTPException, Depends
from app.schemas.sale_product import SaleProductCreate, SaleProductUpdate, SaleProductResponse
from app.services.sale_product_service import SaleProductService
from app.api.dependencies import sale_product_client
from typing import List

def get_sale_product_service() -> SaleProductService:
    return SaleProductService(sale_product_client)

router = APIRouter()

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

@router.put("/{product_id}", response_model=SaleProductResponse)
async def update_sale_product(product_id: int, product: SaleProductUpdate, service: SaleProductService = Depends(get_sale_product_service)):
    updated = service.update_product(product_id, product)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found or update failed")
    return {**product.dict(exclude_unset=True), "id": product_id}

@router.delete("/{product_id}", response_model=dict)
async def delete_sale_product(product_id: int, service: SaleProductService = Depends(get_sale_product_service)):
    deleted = service.delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found or delete failed")
    return {"message": "Product deleted successfully"}
