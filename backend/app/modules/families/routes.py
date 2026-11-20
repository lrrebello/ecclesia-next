from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.models import AuditLog, Family, User
from app.db.base import get_db

router = APIRouter(prefix="/families", tags=["Famílias"])


class FamilyInput(BaseModel):
    name: str
    address: str | None = None
    phone: str | None = None
    observations: str | None = None
    responsible_id: str | None = None


class MemberInput(BaseModel):
    user_id: str


def serialize_family(family: Family) -> dict:
    return {
        "id": family.id,
        "church_id": family.church_id,
        "name": family.name,
        "address": family.address,
        "phone": family.phone,
        "observations": family.observations,
        "responsible_id": family.responsible_id,
        "members": [
            {
                "id": member.id,
                "name": member.name,
                "email": member.email,
                "status": member.status,
            }
            for member in family.members
        ],
    }


@router.get("")
def list_families(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    families = db.query(Family).filter_by(church_id=current_user.church_id).order_by(Family.name).all()
    return {"families": [serialize_family(family) for family in families]}


@router.post("")
def create_family(
    payload: FamilyInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.church_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Usuário não vinculado a uma igreja")

    family = Family(
        church_id=current_user.church_id,
        name=payload.name.strip(),
        address=payload.address,
        phone=payload.phone,
        observations=payload.observations,
        responsible_id=payload.responsible_id,
    )

    if payload.responsible_id:
        responsible = db.query(User).filter_by(
            id=payload.responsible_id,
            church_id=current_user.church_id,
        ).first()

        if not responsible:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Responsável não encontrado")

        family.members.append(responsible)

    db.add(family)
    db.commit()
    db.refresh(family)

    db.add(
        AuditLog(
            user_id=current_user.id,
            church_id=current_user.church_id,
            action="CREATE",
            module="FAMILY",
            description=f"Família criada: {family.name}",
            new_values={"id": family.id, "name": family.name},
        )
    )
    db.commit()

    return serialize_family(family)


@router.get("/{family_id}")
def get_family(
    family_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    family = db.query(Family).filter_by(id=family_id).first()

    if not family or family.church_id != current_user.church_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Família não encontrada")

    return serialize_family(family)


@router.put("/{family_id}")
def update_family(
    family_id: str,
    payload: FamilyInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    family = db.query(Family).filter_by(id=family_id).first()

    if not family or family.church_id != current_user.church_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Família não encontrada")

    old_values = serialize_family(family)

    family.name = payload.name.strip()
    family.address = payload.address
    family.phone = payload.phone
    family.observations = payload.observations
    family.responsible_id = payload.responsible_id

    if payload.responsible_id:
        responsible = db.query(User).filter_by(
            id=payload.responsible_id,
            church_id=current_user.church_id,
        ).first()

        if not responsible:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Responsável não encontrado")

        if responsible not in family.members:
            family.members.append(responsible)

    db.commit()
    db.refresh(family)

    db.add(
        AuditLog(
            user_id=current_user.id,
            church_id=current_user.church_id,
            action="UPDATE",
            module="FAMILY",
            description=f"Família atualizada: {family.name}",
            old_values=old_values,
            new_values=serialize_family(family),
        )
    )
    db.commit()

    return serialize_family(family)


@router.delete("/{family_id}")
def delete_family(
    family_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    family = db.query(Family).filter_by(id=family_id).first()

    if not family or family.church_id != current_user.church_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Família não encontrada")

    for member in family.members:
        member.family_id = None

    family_name = family.name
    db.delete(family)
    db.commit()

    db.add(
        AuditLog(
            user_id=current_user.id,
            church_id=current_user.church_id,
            action="DELETE",
            module="FAMILY",
            description=f"Família excluída: {family_name}",
            old_values={"id": family_id, "name": family_name},
        )
    )
    db.commit()

    return {"success": True}


@router.post("/{family_id}/members")
def add_member(
    family_id: str,
    payload: MemberInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    family = db.query(Family).filter_by(id=family_id).first()

    if not family or family.church_id != current_user.church_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Família não encontrada")

    member = db.query(User).filter_by(
        id=payload.user_id,
        church_id=current_user.church_id,
    ).first()

    if not member:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Membro não encontrado")

    member.family_id = family.id
    db.commit()

    return serialize_family(family)


@router.delete("/{family_id}/members/{user_id}")
def remove_member(
    family_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    family = db.query(Family).filter_by(id=family_id).first()

    if not family or family.church_id != current_user.church_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Família não encontrada")

    member = db.query(User).filter_by(id=user_id).first()

    if not member or member.family_id != family.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Membro não pertence a esta família")

    member.family_id = None

    if family.responsible_id == member.id:
        family.responsible_id = None

    db.commit()

    return serialize_family(family)
