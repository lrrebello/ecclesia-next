from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.models import Ministry, User, AuditLog
from app.db.base import get_db

router = APIRouter(prefix="/ministries", tags=["Ministérios"])


class MinistryInput(BaseModel):
    name: str
    description: str | None = None
    leader_id: str | None = None
    vice_leader_id: str | None = None
    extra_leader_ids: list[str] = []
    is_kids_ministry: bool = False


class MemberInput(BaseModel):
    user_id: str


def serialize_ministry(ministry: Ministry) -> dict:
    return {
        "id": ministry.id,
        "church_id": ministry.church_id,
        "name": ministry.name,
        "description": ministry.description,
        "leader_id": ministry.leader_id,
        "vice_leader_id": ministry.vice_leader_id,
        "extra_leaders": ministry.extra_leaders or [],
        "is_kids_ministry": ministry.is_kids_ministry,
        "is_active": ministry.is_active,
        "members": [
            {"id": member.id, "name": member.name, "email": member.email}
            for member in ministry.members
        ],
    }


def can_manage_ministry(user: User, ministry: Ministry) -> bool:
    if user.church_id != ministry.church_id:
        return False

    if ministry.leader_id == user.id:
        return True

    if ministry.vice_leader_id == user.id:
        return True

    return user.id in (ministry.extra_leaders or [])


@router.get("")
def list_ministries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ministries = db.query(Ministry).filter_by(
        church_id=current_user.church_id,
        is_active=True,
    ).all()

    return {"ministries": [serialize_ministry(ministry) for ministry in ministries]}


@router.post("")
def create_ministry(
    payload: MinistryInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.church_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Usuário não vinculado a uma igreja")

    ministry = Ministry(
        church_id=current_user.church_id,
        name=payload.name.strip(),
        description=payload.description,
        leader_id=payload.leader_id,
        vice_leader_id=payload.vice_leader_id,
        extra_leaders=payload.extra_leader_ids,
        is_kids_ministry=payload.is_kids_ministry,
    )

    if payload.leader_id:
        leader = db.query(User).filter_by(
            id=payload.leader_id,
            church_id=current_user.church_id,
        ).first()
        if leader:
            ministry.members.append(leader)

    if payload.vice_leader_id:
        vice_leader = db.query(User).filter_by(
            id=payload.vice_leader_id,
            church_id=current_user.church_id,
        ).first()
        if vice_leader and vice_leader not in ministry.members:
            ministry.members.append(vice_leader)

    db.add(ministry)
    db.commit()
    db.refresh(ministry)

    db.add(
        AuditLog(
            user_id=current_user.id,
            church_id=current_user.church_id,
            action="CREATE",
            module="MINISTRY",
            description=f"Ministério criado: {ministry.name}",
            new_values={"id": ministry.id, "name": ministry.name},
        )
    )
    db.commit()

    return serialize_ministry(ministry)


@router.get("/{ministry_id}")
def get_ministry(
    ministry_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ministry = db.query(Ministry).filter_by(id=ministry_id).first()

    if not ministry or ministry.church_id != current_user.church_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ministério não encontrado")

    return serialize_ministry(ministry)


@router.put("/{ministry_id}")
def update_ministry(
    ministry_id: str,
    payload: MinistryInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ministry = db.query(Ministry).filter_by(id=ministry_id).first()

    if not ministry or ministry.church_id != current_user.church_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ministério não encontrado")

    if not can_manage_ministry(current_user, ministry):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado")

    old_values = {
        "name": ministry.name,
        "description": ministry.description,
        "leader_id": ministry.leader_id,
        "vice_leader_id": ministry.vice_leader_id,
        "extra_leaders": ministry.extra_leaders,
        "is_kids_ministry": ministry.is_kids_ministry,
    }

    ministry.name = payload.name.strip()
    ministry.description = payload.description
    ministry.leader_id = payload.leader_id
    ministry.vice_leader_id = payload.vice_leader_id
    ministry.extra_leaders = payload.extra_leader_ids
    ministry.is_kids_ministry = payload.is_kids_ministry

    for leader_id in [ministry.leader_id, ministry.vice_leader_id, *(ministry.extra_leaders or [])]:
        if not leader_id:
            continue

        leader = db.query(User).filter_by(
            id=leader_id,
            church_id=current_user.church_id,
        ).first()

        if leader and leader not in ministry.members:
            ministry.members.append(leader)

    db.commit()
    db.refresh(ministry)

    db.add(
        AuditLog(
            user_id=current_user.id,
            church_id=current_user.church_id,
            action="UPDATE",
            module="MINISTRY",
            description=f"Ministério atualizado: {ministry.name}",
            old_values=old_values,
            new_values=serialize_ministry(ministry),
        )
    )
    db.commit()

    return serialize_ministry(ministry)


@router.delete("/{ministry_id}")
def delete_ministry(
    ministry_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ministry = db.query(Ministry).filter_by(id=ministry_id).first()

    if not ministry or ministry.church_id != current_user.church_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ministério não encontrado")

    if not can_manage_ministry(current_user, ministry):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado")

    ministry.is_active = False
    db.commit()

    db.add(
        AuditLog(
            user_id=current_user.id,
            church_id=current_user.church_id,
            action="DELETE",
            module="MINISTRY",
            description=f"Ministério desativado: {ministry.name}",
            old_values={"id": ministry.id, "name": ministry.name},
        )
    )
    db.commit()

    return {"success": True}


@router.post("/{ministry_id}/members")
def add_member(
    ministry_id: str,
    payload: MemberInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ministry = db.query(Ministry).filter_by(id=ministry_id).first()

    if not ministry or ministry.church_id != current_user.church_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ministério não encontrado")

    if not can_manage_ministry(current_user, ministry):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado")

    member = db.query(User).filter_by(
        id=payload.user_id,
        church_id=current_user.church_id,
        status="active",
    ).first()

    if not member:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Membro não encontrado")

    if member not in ministry.members:
        ministry.members.append(member)
        db.commit()

    return serialize_ministry(ministry)


@router.delete("/{ministry_id}/members/{user_id}")
def remove_member(
    ministry_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ministry = db.query(Ministry).filter_by(id=ministry_id).first()

    if not ministry or ministry.church_id != current_user.church_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ministério não encontrado")

    if not can_manage_ministry(current_user, ministry):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado")

    member = db.query(User).filter_by(id=user_id).first()

    if member and member in ministry.members:
        ministry.members.remove(member)
        db.commit()

    return serialize_ministry(ministry)
