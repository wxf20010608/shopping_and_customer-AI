from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..services import user_service

router = APIRouter(prefix="/users", tags=["users"]) 


@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    return user_service.register_user(payload, db)


@router.post("/login", response_model=schemas.UserRead)
def login_user(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    return user_service.login_user(payload, db)


@router.get("/{user_id}", response_model=schemas.UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.get_user(user_id, db)


@router.put("/{user_id}", response_model=schemas.UserRead)
def update_user(user_id: int, payload: schemas.UserUpdate, db: Session = Depends(get_db)):
    return user_service.update_user(user_id, payload, db)


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.delete_user(user_id, db)

