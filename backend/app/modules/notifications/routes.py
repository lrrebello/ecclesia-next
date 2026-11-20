import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.models import AuditLog, Ministry, User
from app.db.base import get_db
from app.modules.notifications.models import Notification, UploadedFile, UserNotification

router = APIRouter(prefix="/notifications", tags=["Notificações e Uploads"])

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": "image",
    "image/png": "image",
    "image/webp": "image",
    "video/mp4": "video",
    "audio/mpeg": "audio",
    "audio/mp3": "audio",
    "application/pdf": "document",
}

MAX_FILE_SIZE = 50 * 1024 * 1024


class NotificationInput(BaseModel):
    title: str
    message: str
    type: str = "general"
    ministry_id: str | None = None
    target_type: str = "all"
    target_user_id: str | None = None
    action_url: str | None = None


def serialize_notification(notification: Notification, delivery: UserNotification | None = None) -> dict:
    return {
        "id": notification.id,
        "title": notification.title,
        "message": notification.message,
        "type": notification.type,
        "action_url": notification.action_url,
        "created_at": notification.created_at,
        "read": delivery.read_at is not None if delivery else False,
    }


@router.get("")
def list_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deliveries = (
        db.query(UserNotification)
        .join(Notification)
        .filter(
            UserNotification.user_id == current_user.id,
            Notification.church_id == current_user.church_id,
            Notification.is_active == True,
        )
        .order_by(Notification.created_at.desc())
        .all()
    )

    return {
        "notifications": [
            serialize_notification(delivery.notification, delivery)
            for delivery in deliveries
        ]
    }


@router.post("")
def create_notification(
    payload: NotificationInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.core.models import Permission, RolePermission, UserRole

    allowed = (
        db.query(User)
        .join(UserRole, UserRole.user_id == User.id)
        .join(RolePermission, RolePermission.role_id == UserRole.role_id)
        .join(Permission, Permission.id == RolePermission.permission_id)
        .filter(
            User.id == current_user.id,
            Permission.code == "admin.manage",
        )
        .first()
    )

    if not allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado")

    ministry = None

    if payload.ministry_id:
        ministry = db.query(Ministry).filter_by(
            id=payload.ministry_id,
            church_id=current_user.church_id,
        ).first()

        if not ministry:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Ministério não encontrado")

    target_user = None

    if payload.target_user_id:
        target_user = db.query(User).filter_by(
            id=payload.target_user_id,
            church_id=current_user.church_id,
        ).first()

        if not target_user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuário não encontrado")

    notification = Notification(
        church_id=current_user.church_id,
        ministry_id=ministry.id if ministry else None,
        title=payload.title.strip(),
        message=payload.message,
        type=payload.type,
        target_type=payload.target_type,
        target_user_id=target_user.id if target_user else None,
        action_url=payload.action_url,
        created_by=current_user.id,
    )

    db.add(notification)
    db.flush()

    if target_user:
        recipients = [target_user]
    elif ministry:
        recipients = ministry.members
    else:
        recipients = db.query(User).filter_by(
            church_id=current_user.church_id,
            status="approved",
        ).all()

    for recipient in recipients:
        db.add(
            UserNotification(
                notification_id=notification.id,
                user_id=recipient.id,
            )
        )

    db.commit()
    db.refresh(notification)

    db.add(
        AuditLog(
            user_id=current_user.id,
            church_id=current_user.church_id,
            action="CREATE",
            module="NOTIFICATION",
            description=f"Notificação criada: {notification.title}",
            new_values={"id": notification.id},
        )
    )
    db.commit()

    return {
        "id": notification.id,
        "title": notification.title,
        "recipients": len(recipients),
    }


@router.post("/{notification_id}/read")
def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delivery = db.query(UserNotification).filter_by(
        notification_id=notification_id,
        user_id=current_user.id,
    ).first()

    if not delivery:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notificação não encontrada")

    if not delivery.read_at:
        from datetime import datetime

        delivery.read_at = datetime.utcnow()
        db.commit()

    return {"id": delivery.id, "read": True}


@router.post("/uploads")
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = Form("document"),
    is_public: bool = Form(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Tipo de arquivo não permitido")

    if file_type not in ["image", "video", "audio", "document"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Tipo de arquivo inválido")

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "O arquivo excede o limite de 50 MB")

    extension = Path(file.filename or "arquivo").suffix.lower()
    safe_name = f"{uuid.uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / safe_name

    with open(file_path, "wb") as output:
        output.write(contents)

    uploaded = UploadedFile(
        church_id=current_user.church_id,
        user_id=current_user.id,
        file_name=safe_name,
        original_name=file.filename or safe_name,
        file_path=str(file_path),
        content_type=file.content_type,
        file_size=len(contents),
        file_type=file_type,
        is_public=is_public,
    )

    db.add(uploaded)
    db.commit()
    db.refresh(uploaded)

    return {
        "id": uploaded.id,
        "file_name": uploaded.file_name,
        "original_name": uploaded.original_name,
        "file_type": uploaded.file_type,
        "file_size": uploaded.file_size,
        "url": f"/api/v1/notifications/uploads/{uploaded.id}",
    }


@router.get("/uploads/{file_id}")
def get_uploaded_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from fastapi.responses import FileResponse

    uploaded = db.query(UploadedFile).filter_by(
        id=file_id,
        church_id=current_user.church_id,
    ).first()

    if not uploaded:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Arquivo não encontrado")

    if not uploaded.is_public and uploaded.user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado")

    return FileResponse(uploaded.file_path, filename=uploaded.original_name)
