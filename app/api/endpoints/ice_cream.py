from fastapi import APIRouter, Query, HTTPException, Depends
from app.schemas.ice_cream_schema import IceCreamCreate, IceCreamResponse
from app.services.ice_cream_service import IceCreamService
from app.api.dependencies import ice_cream_client
from typing import List

def get_ice_cream_service() -> IceCreamService:
    return IceCreamService(ice_cream_client)

router = APIRouter()

@router.get("/", response_model=List[IceCreamResponse])
async def get_ice_creams(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: IceCreamService = Depends(get_ice_cream_service)
):
    """
    페이징된 판매 상품 목록을 가져오는 API.
    """
    offset = (page - 1) * page_size
    ice_creams = service.get_ice_creams(offset=offset, limit=page_size)
    
    if not ice_creams:
        raise HTTPException(status_code=404, detail="No Ice-Cream found.")
    
    return ice_creams

@router.post("/", response_model=IceCreamResponse)
async def create_ice_cream(ice_cream: IceCreamCreate, service: IceCreamService = Depends(get_ice_cream_service)):
    ice_cream_id = service.create_ice_cream(ice_cream)
    return {**ice_cream.dict(), "id": ice_cream_id}

@router.get("/{ice_cream_id}", response_model=IceCreamResponse)
async def get_ice_cream(ice_cream_id: int, service: IceCreamService = Depends(get_ice_cream_service)):
    ice_cream = service.get_ice_cream(ice_cream_id)
    if ice_cream is None:
        raise HTTPException(status_code=404, detail="Ice cream not found")
    return ice_cream

@router.delete("/{ice_cream_id}", response_model=dict)
async def delete_ice_cream(ice_cream_id: int, service: IceCreamService = Depends(get_ice_cream_service)):
    deleted = service.delete_ice_cream(ice_cream_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ice cream not found or delete failed")
    return {"message": "Ice cream deleted successfully"}
