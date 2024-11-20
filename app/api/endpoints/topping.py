from fastapi import APIRouter, Query, HTTPException, Depends, File, UploadFile
from app.schemas.topping_schema import ToppingCreate, ToppingResponse, ToppingResponseWithImg
from app.services.topping_service import ToppingService
from app.api.dependencies import topping_client
from typing import List
from PIL import Image
from io import BytesIO

def get_topping_service() -> ToppingService:
    return ToppingService(topping_client)

router = APIRouter()

@router.get("/", response_model=List[ToppingResponseWithImg])
async def get_toppings(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: ToppingService = Depends(get_topping_service)
):
    """
    페이징된 토핑 목록을 가져오는 API.
    """
    offset = (page - 1) * page_size
    toppings = service.get_toppings(offset=offset, limit=page_size)
    
    if not toppings:
        raise HTTPException(status_code=404, detail="No toppings found.")
    
    return toppings

@router.post("/", response_model=ToppingResponse)
async def create_topping(topping: ToppingCreate = Depends(ToppingCreate.as_form),
    image: UploadFile = File(...), service: ToppingService = Depends(get_topping_service)):
    image_bytes = await image.read()
    pil_image = Image.open(BytesIO(image_bytes))
    topping_id = service.create_topping(topping, pil_image)
    return {
        "topping_id": topping_id,
        "name": topping.name,
        "extra_price": topping.extra_price

    }

@router.get("/{topping_id}", response_model=ToppingResponse)
async def get_topping(topping_id: int, service: ToppingService = Depends(get_topping_service)):
    topping = service.get_topping(topping_id)
    if topping is None:
        raise HTTPException(status_code=404, detail="Topping not found")
    return topping

@router.delete("/{topping_id}", response_model=dict)
async def delete_topping(topping_id: int, service: ToppingService = Depends(get_topping_service)):
    deleted = service.delete_topping(topping_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Topping not found or delete failed")
    return {"message": "Topping deleted successfully"}
