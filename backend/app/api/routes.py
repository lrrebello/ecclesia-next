from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.base import get_db
from app.core.models import User, Church, AuditLog, UserRole, RolePermission, Permission
from app.security.password import hash_password, verify_password
from app.security.tokens import create_access_token, create_refresh_token
import uuid

router = APIRouter()


class RegisterInput(BaseModel):
    church_slug: str
    name: str
    email: EmailStr
    password: str
    data_consent: bool


class LoginInput(BaseModel):
    email: EmailStr
    password: str


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/auth/register")
def register(payload: RegisterInput, db: Session = Depends(get_db)):
    if not payload.data_consent:
        raise HTTPException(400, "Consentimento de dados é obrigatório")

    church = db.query(Church).filter_by(slug=payload.church_slug).first()
    if not church:
        raise HTTPException(404, "Igreja não encontrada")

    if db.query(User).filter_by(email=payload.email.lower()).first():
        raise HTTPException(409, "E-mail já cadastrado")

    user = User(
        church_id=church.id,
        name=payload.name.strip(),
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        status="pending",
        email_verification_token=str(uuid.uuid4()),
        data_consent_at=None,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "status": user.status,
        "email_verification_token": user.email_verification_token,
    }


@router.post("/auth/login")
def login(payload: LoginInput, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=payload.email.lower()).first()

    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "E-mail ou senha inválidos")

    if user.status not in ["active", "approved"] or not user.is_email_verified:
        raise HTTPException(403, "Conta pendente, rejeitada ou e-mail não verificado")

    return {
        "access_token": create_access_token(user.id, user.church_id),
        "refresh_token": create_refresh_token(user.id),
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
    }


@router.get("/auth/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "status": current_user.status,
        "church_id": current_user.church_id,
    }


@router.get("/auth/permissions")
def permissions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(Permission.code, UserRole.scope_type, UserRole.scope_id)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(UserRole, UserRole.role_id == RolePermission.role_id)
        .filter(UserRole.user_id == current_user.id)
        .all()
    )

    return {
        "permissions": [
            {
                "code": code,
                "scope_type": scope_type,
                "scope_id": scope_id,
            }
            for code, scope_type, scope_id in rows
        ]
    }
