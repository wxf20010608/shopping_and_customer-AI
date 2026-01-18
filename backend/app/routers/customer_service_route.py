from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas
from ..services import customer_service
import os
from ..utils import load_env

router = APIRouter(prefix="/customer-service", tags=["customer-service"]) 


@router.post("/chat", response_model=schemas.ChatMessageRead, status_code=status.HTTP_201_CREATED)
def chat(payload: schemas.ChatMessageCreate, db: Session = Depends(get_db)):
    msg = customer_service.chat(payload.user_id, payload.product_id, payload.message, db, getattr(payload, "model", None))
    return msg


@router.get("/history/{user_id}/{product_id}", response_model=schemas.ChatHistoryRead)
def history(user_id: int, product_id: int, start: str | None = None, end: str | None = None, limit: int = 100, db: Session = Depends(get_db)):
    pid = None if product_id == 0 else product_id
    items = customer_service.history(user_id, pid, db, start, end, limit)
    return {"items": items}


@router.post("/chat/upload", response_model=schemas.ChatMessageRead, status_code=status.HTTP_201_CREATED)
def chat_upload(
    user_id: int = Form(...),
    product_id: int | None = Form(None),
    message: str = Form(""),
    images: list[UploadFile] = File(None),
    files: list[UploadFile] = File(None),
    audios: list[UploadFile] = File(None),
    model: str | None = Form(None),
    db: Session = Depends(get_db)
):
    msg = customer_service.chat_with_upload(user_id, product_id, message, images, files, audios, db, model)
    return msg


@router.delete("/history/{user_id}/{product_id}")
def clear_history(user_id: int, product_id: int, db: Session = Depends(get_db)):
    pid = None if product_id == 0 else product_id
    deleted = customer_service.delete_conversation(user_id, pid, db)
    return {"deleted": deleted}


@router.delete("/message/{message_id}")
def retract_message(message_id: int, user_id: int, db: Session = Depends(get_db)):
    ok = customer_service.retract_message(message_id, user_id, db)
    if not ok:
        return {"deleted": False}
    return {"deleted": True}


@router.get("/status")
def ai_status():
    load_env()
    configured = bool(os.environ.get("MODEL_API_KEY") or os.environ.get("DASHSCOPE_API_KEY"))
    return {
        "configured": configured,
        "model_text": os.environ.get("MODEL_NAME_TEXT"),
        "model_vl": os.environ.get("MODEL_NAME_VL"),
        "model_stt": os.environ.get("MODEL_NAME_STT"),
        "base_url": os.environ.get("MODEL_BASE_URL"),
        "source": os.environ.get("ENV_LOADED_PATH"),
    }