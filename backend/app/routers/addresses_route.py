from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..services import address_service

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.get("/{user_id}", response_model=List[schemas.AddressRead])
def list_addresses(user_id: int, db: Session = Depends(get_db)):
    return address_service.list_addresses(user_id, db)


@router.post("/{user_id}", response_model=schemas.AddressRead, status_code=status.HTTP_201_CREATED)
def create_address(user_id: int, payload: schemas.AddressCreate, db: Session = Depends(get_db)):
    return address_service.create_address(user_id, payload, db)


@router.put("/{user_id}/{address_id}", response_model=schemas.AddressRead)
def update_address(user_id: int, address_id: int, payload: schemas.AddressUpdate, db: Session = Depends(get_db)):
    return address_service.update_address(user_id, address_id, payload, db)


@router.delete("/{user_id}/{address_id}")
def delete_address(user_id: int, address_id: int, db: Session = Depends(get_db)):
    return address_service.delete_address(user_id, address_id, db)