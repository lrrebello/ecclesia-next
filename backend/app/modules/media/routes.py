from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.models import Ministry, User, AuditLog
from app.db.base import get_db
from app.modules.media.models import Devotional, DevotionalReading, MediaAlbum, MediaItem

router = APIRouter(prefix="/media", tags=["Mídia e Devocionais"])


class AlbumInput(BaseModel):
    title: str
    description: str | None = None
    cover_image: str | None = None
    ministry_id: str | None = None
    is_public: bool = True


class MediaItemInput(BaseModel):
    album_id: str
    title: str
    description: str | None = None
    media_type: str
    file_path: str | None = None
    external_url: str | None = None
    thumbnail_path: str | None = None
    file_size: int | None = None
    duration_seconds: int | None = None
    is_public: bool = True


class DevotionalInput(BaseModel):
    title: str
    scripture_reference: str | None = None
    scripture_text: str | None = None
    content: str
    prayer: str | None = None
    ministry_id: str | None = None
    publish_date: str | None = None
    is_published: bool = False


def serialize_album(album: MediaAlbum) -> dict:
    return {
        "id": album.id,
        "title": album.title,
        "description": album.description,
        "cover_image": album.cover_image,
        "ministry_id": album.ministry_id,
        "is_public": album.is_public,
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "media_type": item.media_type,
                "file_path": item.file_path,
                "external_url": item.external_url,
                "thumbnail_path": item.thumbnail_path,
            }
            for item in album.items
            if item.is_active
        ],
    }


def serialize_devotional(devotional: Devotional, current_user: User | None = None) -> dict:
    read = False

    if current_user:
        read = any(reading.user_id == current_user.id for reading in devotional.readings)

    return {
        "id": devotional.id,
        "title": devotional.title,
        "scripture_reference": devotional.scripture_reference,
        "scripture_text": devotional.scripture_text,
        "content": devotional.content,
        "prayer": devotional.prayer,
        "publish_date": devotional.publish_date,
        "is_published": devotional.is_published,
        "read": read,
    }


@router.get("/albums")
def list_albums(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    albums = db.query(MediaAlbum).filter_by(
        church_id=current_user.church_id,
        is_active=True,
    ).order_by(MediaAlbum.created_at.desc()).all()

    return {"albums": [serialize_album(album) for album in albums]}


@router.post("/albums")
def create_album(
    payload: AlbumInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ministry = None

    if payload.ministry_id:
        ministry = db.query(Ministry).filter_by(
            id=payload.ministry_id,
            church_id=current_user.church_id,
        ).first()

        if not ministry:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Ministério não encontrado")

    album = MediaAlbum(
        church_id=current_user.church_id,
        ministry_id=ministry.id if ministry else None,
        title=payload.title.strip(),
        description=payload.description,
        cover_image=payload.cover_image,
        is_public=payload.is_public,
        created_by=current_user.id,
    )

    db.add(album)
    db.commit()
    db.refresh(album)

    return serialize_album(album)


@router.post("/albums/{album_id}/items")
def create_media_item(
    album_id: str,
    payload: MediaItemInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    album = db.query(MediaAlbum).filter_by(
        id=album_id,
        church_id=current_user.church_id,
    ).first()

    if not album:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Álbum não encontrado")

    if payload.media_type not in ["image", "video", "audio", "document"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Tipo de mídia inválido")

    if not payload.file_path and not payload.external_url:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Informe um arquivo ou URL externa")

    item = MediaItem(
        church_id=current_user.church_id,
        album_id=album.id,
        title=payload.title.strip(),
        description=payload.description,
        media_type=payload.media_type,
        file_path=payload.file_path,
        external_url=payload.external_url,
        thumbnail_path=payload.thumbnail_path,
        file_size=payload.file_size,
        duration_seconds=payload.duration_seconds,
        is_public=payload.is_public,
        created_by=current_user.id,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    db.add(
        AuditLog(
            user_id=current_user.id,
            church_id=current_user.church_id,
            action="CREATE",
            module="MEDIA",
            description=f"Mídia criada: {item.title}",
            new_values={"id": item.id, "album_id": album.id},
        )
    )
    db.commit()

    return {
        "id": item.id,
        "title": item.title,
        "media_type": item.media_type,
        "file_path": item.file_path,
        "external_url": item.external_url,
    }


@router.get("/devotionals")
def list_devotionals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    devotionals = db.query(Devotional).filter_by(
        church_id=current_user.church_id,
        is_active=True,
        is_published=True,
    ).order_by(Devotional.publish_date.desc()).all()

    return {
        "devotionals": [
            serialize_devotional(devotional, current_user)
            for devotional in devotionals
        ]
    }


@router.post("/devotionals")
def create_devotional(
    payload: DevotionalInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ministry = None

    if payload.ministry_id:
        ministry = db.query(Ministry).filter_by(
            id=payload.ministry_id,
            church_id=current_user.church_id,
        ).first()

        if not ministry:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Ministério não encontrado")

    publish_date = None

    if payload.publish_date:
        publish_date = datetime.strptime(payload.publish_date, "%Y-%m-%d").date()

    devotional = Devotional(
        church_id=current_user.church_id,
        ministry_id=ministry.id if ministry else None,
        title=payload.title.strip(),
        scripture_reference=payload.scripture_reference,
        scripture_text=payload.scripture_text,
        content=payload.content,
        prayer=payload.prayer,
        author_id=current_user.id,
        publish_date=publish_date,
        is_published=payload.is_published,
    )

    db.add(devotional)
    db.commit()
    db.refresh(devotional)

    db.add(
        AuditLog(
            user_id=current_user.id,
            church_id=current_user.church_id,
            action="CREATE",
            module="DEVOTIONAL",
            description=f"Devocional criado: {devotional.title}",
            new_values={"id": devotional.id},
        )
    )
    db.commit()

    return serialize_devotional(devotional, current_user)


@router.post("/devotionals/{devotional_id}/read")
def mark_devotional_read(
    devotional_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    devotional = db.query(Devotional).filter_by(
        id=devotional_id,
        church_id=current_user.church_id,
        is_active=True,
    ).first()

    if not devotional:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Devocional não encontrado")

    existing = db.query(DevotionalReading).filter_by(
        devotional_id=devotional.id,
        user_id=current_user.id,
    ).first()

    if existing:
        return {"id": existing.id, "already_read": True}

    reading = DevotionalReading(
        devotional_id=devotional.id,
        user_id=current_user.id,
    )

    db.add(reading)
    db.commit()
    db.refresh(reading)

    return {"id": reading.id, "already_read": False}
