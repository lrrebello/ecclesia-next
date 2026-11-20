from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.models import AuditLog, Event, Ministry, User
from app.db.base import get_db

router = APIRouter(prefix="/events", tags=["Eventos"])


class EventInput(BaseModel):
    title: str
    description: str | None = None
    start_at: datetime
    end_at: datetime | None = None
    location: str | None = None
    ministry_id: str | None = None
    recurrence_type: str = "none"
    recurrence_interval: int = 1
    recurrence_until: date | None = None
    is_public: bool = True


def serialize_event(event: Event) -> dict:
    return {
        "id": event.id,
        "church_id": event.church_id,
        "ministry_id": event.ministry_id,
        "title": event.title,
        "description": event.description,
        "start_at": event.start_at,
        "end_at": event.end_at,
        "location": event.location,
        "recurrence_type": event.recurrence_type,
        "recurrence_interval": event.recurrence_interval,
        "recurrence_until": event.recurrence_until,
        "is_public": event.is_public,
        "ministry": {
            "id": event.ministry.id,
            "name": event.ministry.name,
        }
        if event.ministry
        else None,
    }


def can_manage_ministry(user: User, ministry: Ministry | None) -> bool:
    if not ministry:
        return True

    if ministry.church_id != user.church_id:
        return False

    if ministry.leader_id == user.id:
        return True

    if ministry.vice_leader_id == user.id:
        return True

    return user.id in (ministry.extra_leaders or [])


def expand_occurrences(event: Event, limit: int = 50) -> list[dict]:
    if event.recurrence_type == "none":
        return [serialize_event(event)]

    occurrences = []
    current_start = event.start_at
    current_end = event.end_at
    interval = max(event.recurrence_interval or 1, 1)
    until = event.recurrence_until or (event.start_at.date() + timedelta(days=365))

    for _ in range(limit):
        if current_start.date() > until:
            break

        occurrence = serialize_event(event)
        occurrence["start_at"] = current_start
        occurrence["end_at"] = current_end
        occurrences.append(occurrence)

        if event.recurrence_type == "daily":
            current_start += timedelta(days=interval)
            current_end = current_end + timedelta(days=interval) if current_end else None
        elif event.recurrence_type == "weekly":
            current_start += timedelta(weeks=interval)
            current_end = current_end + timedelta(weeks=interval) if current_end else None
        elif event.recurrence_type == "monthly":
            month = current_start.month + interval
            year = current_start.year + (month - 1) // 12
            month = (month - 1) % 12 + 1
            current_start = current_start.replace(year=year, month=month)
            current_end = (
                current_end.replace(year=year, month=month)
                if current_end
                else None
            )
        else:
            break

    return occurrences


@router.get("/public")
def list_public_events(db: Session = Depends(get_db)):
    events = db.query(Event).filter(
        Event.is_active == True,
        Event.is_public == True,
        Event.start_at >= datetime.utcnow(),
    ).order_by(Event.start_at.asc()).limit(50).all()

    result = []
    for event in events:
        result.extend(expand_occurrences(event, limit=10))

    return {"events": result}


@router.get("")
def list_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ministry_ids = [ministry.id for ministry in current_user.ministries]

    events = db.query(Event).filter(
        Event.church_id == current_user.church_id,
        Event.is_active == True,
        or_(
            Event.ministry_id.is_(None),
            Event.ministry_id.in_(ministry_ids),
        ),
    ).order_by(Event.start_at.asc()).all()

    result = []
    for event in events:
        result.extend(expand_occurrences(event, limit=20))

    return {"events": result}


@router.post("")
def create_event(
    payload: EventInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.church_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Usuário não vinculado a uma filial")

    ministry = None

    if payload.ministry_id:
        ministry = db.query(Ministry).filter_by(
            id=payload.ministry_id,
            church_id=current_user.church_id,
        ).first()

        if not ministry:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Ministério não encontrado")

        if not can_manage_ministry(current_user, ministry):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Você não pode criar eventos neste ministério")

    if payload.end_at and payload.end_at <= payload.start_at:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "A data final deve ser posterior à inicial")

    event = Event(
        church_id=current_user.church_id,
        ministry_id=ministry.id if ministry else None,
        title=payload.title.strip(),
        description=payload.description,
        start_at=payload.start_at,
        end_at=payload.end_at,
        location=payload.location,
        recurrence_type=payload.recurrence_type,
        recurrence_interval=payload.recurrence_interval,
        recurrence_until=payload.recurrence_until,
        is_public=payload.is_public,
        created_by=current_user.id,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    db.add(
        AuditLog(
            user_id=current_user.id,
            church_id=current_user.church_id,
            action="CREATE",
            module="EVENT",
            description=f"Evento criado: {event.title}",
            new_values={"id": event.id, "title": event.title},
        )
    )
    db.commit()

    return serialize_event(event)


@router.get("/{event_id}")
def get_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = db.query(Event).filter_by(id=event_id).first()

    if not event or event.church_id != current_user.church_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Evento não encontrado")

    return serialize_event(event)


@router.put("/{event_id}")
def update_event(
    event_id: str,
    payload: EventInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = db.query(Event).filter_by(id=event_id).first()

    if not event or event.church_id != current_user.church_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Evento não encontrado")

    if not can_manage_ministry(current_user, event.ministry):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado")

    old_values = serialize_event(event)

    event.title = payload.title.strip()
    event.description = payload.description
    event.start_at = payload.start_at
    event.end_at = payload.end_at
    event.location = payload.location
    event.recurrence_type = payload.recurrence_type
    event.recurrence_interval = payload.recurrence_interval
    event.recurrence_until = payload.recurrence_until
    event.is_public = payload.is_public

    db.commit()
    db.refresh(event)

    db.add(
        AuditLog(
            user_id=current_user.id,
            church_id=current_user.church_id,
            action="UPDATE",
            module="EVENT",
            description=f"Evento atualizado: {event.title}",
            old_values=old_values,
            new_values=serialize_event(event),
        )
    )
    db.commit()

    return serialize_event(event)


@router.delete("/{event_id}")
def delete_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = db.query(Event).filter_by(id=event_id).first()

    if not event or event.church_id != current_user.church_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Evento não encontrado")

    if not can_manage_ministry(current_user, event.ministry):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado")

    event.is_active = False
    db.commit()

    db.add(
        AuditLog(
            user_id=current_user.id,
            church_id=current_user.church_id,
            action="DELETE",
            module="EVENT",
            description=f"Evento desativado: {event.title}",
            old_values={"id": event.id, "title": event.title},
        )
    )
    db.commit()

    return {"success": True}
