import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, DateTime, Date, ForeignKey, Integer, Text, Numeric, JSON, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def uuid_default():
    return str(uuid.uuid4())


member_ministries = Table(
    "member_ministries",
    Base.metadata,
    Column("user_id", String(36), ForeignKey("users.id"), primary_key=True),
    Column("ministry_id", String(36), ForeignKey("ministries.id"), primary_key=True),
)


class Church(Base):
    __tablename__ = "churches"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    country: Mapped[str | None] = mapped_column(String(80))
    currency_code: Mapped[str] = mapped_column(String(3), default="EUR")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    users = relationship("User", back_populates="church")
    ministries = relationship("Ministry", back_populates="church")


class Role(Base):
    __tablename__ = "roles"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    church_id: Mapped[str | None] = mapped_column(ForeignKey("churches.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    users = relationship("UserRole", back_populates="role")


class Permission(Base):
    __tablename__ = "permissions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    code: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class RolePermission(Base):
    __tablename__ = "role_permissions"
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    permission_id: Mapped[str] = mapped_column(ForeignKey("permissions.id"), primary_key=True)


class Family(Base):
    __tablename__ = "families"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    church_id: Mapped[str] = mapped_column(ForeignKey("churches.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    members = relationship("User", back_populates="family")


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    church_id: Mapped[str | None] = mapped_column(ForeignKey("churches.id"))
    family_id: Mapped[str | None] = mapped_column(ForeignKey("families.id"))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255))

    birth_date: Mapped[date | None] = mapped_column(Date)
    baptism_date: Mapped[date | None] = mapped_column(Date)
    conversion_date: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(30))
    marital_status: Mapped[str | None] = mapped_column(String(50))
    spouse_name: Mapped[str | None] = mapped_column(String(160))
    documents: Mapped[str | None] = mapped_column(String(200))
    tax_id: Mapped[str | None] = mapped_column(String(30))
    address: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(50))
    profile_photo: Mapped[str | None] = mapped_column(String(255))
    postal_code: Mapped[str | None] = mapped_column(String(30))
    concelho: Mapped[str | None] = mapped_column(String(120))
    localidade: Mapped[str | None] = mapped_column(String(120))
    education_level: Mapped[str | None] = mapped_column(String(120))
    observations: Mapped[str | None] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String(20), default="pending")
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verification_token: Mapped[str | None] = mapped_column(String(255), unique=True)
    reset_password_token: Mapped[str | None] = mapped_column(String(255), unique=True)
    reset_password_expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    data_consent_at: Mapped[datetime | None] = mapped_column(DateTime)
    marketing_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    church = relationship("Church", back_populates="users")
    family = relationship("Family", back_populates="members")
    roles = relationship("UserRole", back_populates="user")
    ministries = relationship(
        "Ministry",
        secondary=member_ministries,
        back_populates="members",
    )


class UserRole(Base):
    __tablename__ = "user_roles"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    scope_type: Mapped[str] = mapped_column(String(20), default="church")
    scope_id: Mapped[str | None] = mapped_column(String(36))
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")


class Ministry(Base):
    __tablename__ = "ministries"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    church_id: Mapped[str] = mapped_column(ForeignKey("churches.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    leader_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    vice_leader_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    extra_leaders: Mapped[list | None] = mapped_column(JSON, default=list)
    is_kids_ministry: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=datetime.utcnow)

    church = relationship("Church", back_populates="ministries")
    leader = relationship("User", foreign_keys=[leader_id])
    vice_leader = relationship("User", foreign_keys=[vice_leader_id])
    members = relationship(
        "User",
        secondary=member_ministries,
        back_populates="ministries",
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    church_id: Mapped[str | None] = mapped_column(ForeignKey("churches.id"))
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    module: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    old_values: Mapped[dict | None] = mapped_column(JSON)
    new_values: Mapped[dict | None] = mapped_column(JSON)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
