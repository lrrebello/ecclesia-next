from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.models import Church, Family, User, AuditLog, UserRole, RolePermission, Permission
from app.db.base import get_db
from app.security.password import hash_password
import uuid

router = APIRouter(prefix="/members", tags=["Membros"])


class MemberRegisterInput(BaseModel):
    branch_slug: str
    name: str
    email: EmailStr
    password: str
    birth_date: date | None = None
    baptism_date: date | None = None
    conversion_date: date | None = None
    gender: str | None = None
    marital_status: str | None = None
    spouse_name: str | None = None
    documents: str | None = None
    tax_id: str | None = None
    address: str | None = None
    phone: str | None = None
    postal_code: str | None = None
    concelho: str | None = None
    localidade: str | None = None
    education_level: str | None = None
    observations: str | None = None
    data_consent: bool
    marketing_consent: bool = False


class ProfileUpdateInput(BaseModel):
    name: str
    birth_date: date | None = None
    baptism_date: date | None = None
    conversion_date: date | None = None
    gender: str | None = None
    marital_status: str | None = None
    spouse_name: str | None = None
    documents: str | None = None
    tax_id: str | None = None
    address: str | None = None
    phone: str | None = None
    postal_code: str | None = None
    concelho: str | None = None
    localidade: str | None = None
    education_level: str | None = None
    observations: str | None = None


class ApprovalInput(BaseModel):
    action: str


def serialize_member(user: User, include_sensitive: bool = False) -> dict:
    data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "status": user.status,
        "church_id": user.church_id,
        "family_id": user.family_id,
        "birth_date": user.birth_date,
        "baptism_date": user.baptism_date,
        "conversion_date": user.conversion_date,
        "gender": user.gender,
        "marital_status": user.marital_status,
        "spouse_name": user.spouse_name,
        "phone": user.phone,
        "postal_code": user.postal_code,
        "concelho": user.concelho,
        "localidade": user.localidade,
        "education_level": user.education_level,
        "profile_photo": user.profile_photo,
        "created_at": user.created_at,
    }

    if include_sensitive:
        data.update(
            {
                "documents": user.documents,
                "tax_id": user.tax_id,
                "address": user.address,
                "observations": user.observations,
            }
        )

    return data


def can_approve_members(user: User, db: Session) -> bool:
    return (
        db.query(User)
        .join(UserRole, UserRole.user_id == User.id)
        .join(RolePermission, RolePermission.role_id == UserRole.role_id)
        .join(Permission, Permission.id == RolePermission.permission_id)
        .filter(
            User.id == user.id,
            Permission.code == "member.approve",
        )
        .first()
        is not None
    )


@router.post("/register")
def register_member(payload: MemberRegisterInput, db: Session = Depends(get_db)):
    if not payload.data_consent:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Consentimento de dados é obrigatório")

    branch = db.query(Church).filter_by(
        slug=payload.branch_slug,
        is_active=True,
    ).first()

    if not branch:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Filial não encontrada")

    if db.query(User).filter_by(email=payload.email.lower()).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "E-mail já cadastrado")

    user = User(
        church_id=branch.id,
        name=payload.name.strip(),
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        birth_date=payload.birth_date,
        baptism_date=payload.baptism_date,
        conversion_date=payload.conversion_date,
        gender=payload.gender,
        marital_status=payload.marital_status,
        spouse_name=payload.spouse_name if payload.marital_status == "Casado(a)" else None,
        documents=payload.documents,
        tax_id=payload.tax_id,
        address=payload.address,
        phone=payload.phone,
        postal_code=payload.postal_code,
        concelho=payload.concelho,
        localidade=payload.localidade,
        education_level=payload.education_level,
        observations=payload.observations,
        status="pending",
        is_email_verified=False,
        email_verification_token=str(uuid.uuid4()),
        data_consent_at=datetime.utcnow() if payload.data_consent else None,
        marketing_consent=payload.marketing_consent,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    db.add(
        AuditLog(
            user_id=user.id,
            church_id=branch.id,
            action="CREATE",
            module="MEMBERS",
            description=f"Novo cadastro pendente na filial {branch.name}: {user.name}",
            new_values={"id": user.id, "email": user.email},
        )
    )
    db.commit()

    return {
        "id": user.id,
        "status": user.status,
        "email_verification_token": user.email_verification_token,
    }


@router.get("/me")
def my_profile(current_user: User = Depends(get_current_user)):
    return serialize_member(current_user, include_sensitive=True)


@router.put("/me")
def update_my_profile(
    payload: ProfileUpdateInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    old_values = serialize_member(current_user, include_sensitive=True)

    current_user.name = payload.name.strip()
    current_user.birth_date = payload.birth_date
    current_user.baptism_date = payload.baptism_date
    current_user.conversion_date = payload.conversion_date
    current_user.gender = payload.gender
    current_user.marital_status = payload.marital_status
    current_user.spouse_name = payload.spouse_name if payload.marital_status == "Casado(a)" else None
    current_user.documents = payload.documents
    current_user.tax_id = payload.tax_id
    current_user.address = payload.address
    current_user.phone = payload.phone
    current_user.postal_code = payload.postal_code
    current_user.concelho = payload.concelho
    current_user.localidade = payload.localidade
    current_user.education_level = payload.education_level
    current_user.observations = payload.observations

    db.commit()
    db.refresh(current_user)

    db.add(
        AuditLog(
            user_id=current_user.id,
            church_id=current_user.church_id,
            action="UPDATE",
            module="PROFILE",
            description="Perfil atualizado",
            old_values=old_values,
            new_values=serialize_member(current_user, include_sensitive=True),
        )
    )
    db.commit()

    return serialize_member(current_user, include_sensitive=True)


@router.get("")
def list_members(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    members = db.query(User).filter_by(church_id=current_user.church_id).order_by(User.name).all()
    return {"members": [serialize_member(member) for member in members]}


@router.get("/pending")
def list_pending_members(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not can_approve_members(current_user, db):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado")

    members = db.query(User).filter_by(
        church_id=current_user.church_id,
        status="pending",
    ).order_by(User.created_at.desc()).all()

    return {"members": [serialize_member(member) for member in members]}


@router.post("/{member_id}/approval")
def approve_or_reject_member(
    member_id: str,
    payload: ApprovalInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not can_approve_members(current_user, db):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado")

    member = db.query(User).filter_by(
        id=member_id,
        church_id=current_user.church_id,
    ).first()

    if not member:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Membro não encontrado")

    if member.status != "pending":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Somente cadastros pendentes podem ser analisados")

    old_status = member.status

    if payload.action == "approve":
        member.status = "active"
        action = "APPROVE"
        description = f"Membro aprovado: {member.name}"
    elif payload.action == "reject":
        member.status = "rejected"
        action = "REJECT"
        description = f"Membro rejeitado: {member.name}"
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Ação inválida")

    db.commit()

    db.add(
        AuditLog(
            user_id=current_user.id,
            church_id=current_user.church_id,
            action=action,
            module="MEMBERS",
            description=description,
            old_values={"status": old_status},
            new_values={"status": member.status},
        )
    )
    db.commit()

    return serialize_member(member)
