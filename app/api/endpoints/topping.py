from fastapi import APIRouter, HTTPException, Depends
from app.schemas.topping_schema import ToppingCreate, ToppingUpdate, ToppingResponse
from app.services.topping_service import ToppingService
from app.api.dependencies import topping_client
from typing import List

def get_topping_service() -> ToppingService:
    return ToppingService(topping_client)

router = APIRouter()

@router.post("/", response_model=ToppingResponse)
async def create_topping(topping: ToppingCreate, service: ToppingService = Depends(get_topping_service)):
    topping_id = service.create_topping(topping)
    return {**topping.dict(), "id": topping_id}

@router.get("/{topping_id}", response_model=ToppingResponse)
async def get_topping(topping_id: int, service: ToppingService = Depends(get_topping_service)):
    topping = service.get_topping(topping_id)
    if topping is None:
        raise HTTPException(status_code=404, detail="Topping not found")
    return topping

@router.put("/{topping_id}", response_model=ToppingResponse)
async def update_topping(topping_id: int, topping: ToppingUpdate, service: ToppingService = Depends(get_topping_service)):
    updated = service.update_topping(topping_id, topping)
    if not updated:
        raise HTTPException(status_code=404, detail="Topping not found or update failed")
    return {**topping.dict(exclude_unset=True), "id": topping_id}

@router.delete("/{topping_id}", response_model=dict)
async def delete_topping(topping_id: int, service: ToppingService = Depends(get_topping_service)):
    deleted = service.delete_topping(topping_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Topping not found or delete failed")
    return {"message": "Topping deleted successfully"}
