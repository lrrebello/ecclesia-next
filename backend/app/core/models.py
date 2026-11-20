import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, Date, ForeignKey, Integer, Text, Numeric, JSON, Table, Column, text
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
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("churches.id"))
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(30), default="branch", server_default=text("'branch'"))
    country: Mapped[str | None] = mapped_column(String(80))
    currency_code: Mapped[str] = mapped_column(String(3), default="EUR")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    parent = relationship("Church", remote_side=[id], backref="branches")
    users = relationship("User", back_populates="church")
    ministries = relationship("Ministry", back_populates="church")
    families = relationship("Family", back_populates="church")
    events = relationship("Event", back_populates="church")
    financial_accounts = relationship("FinancialAccount", back_populates="church")
    transaction_categories = relationship("TransactionCategory", back_populates="church")
    payment_methods = relationship("PaymentMethod", back_populates="church")
    transactions = relationship("Transaction", back_populates="church")
    bills = relationship("Bill", back_populates="church")


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
    responsible_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    address: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(50))
    observations: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=datetime.utcnow)

    church = relationship("Church", back_populates="families")
    responsible = relationship("User", foreign_keys=[responsible_id])
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

    church = relationship("Church", back_populates="users", foreign_keys=[church_id])
    family = relationship("Family", back_populates="members", foreign_keys=[family_id])
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
    events = relationship("Event", back_populates="ministry")
    transactions = relationship("Transaction", back_populates="ministry")


class Event(Base):
    __tablename__ = "events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    church_id: Mapped[str] = mapped_column(ForeignKey("churches.id"), nullable=False)
    ministry_id: Mapped[str | None] = mapped_column(ForeignKey("ministries.id"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    start_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_at: Mapped[datetime | None] = mapped_column(DateTime)
    location: Mapped[str | None] = mapped_column(String(255))
    recurrence_type: Mapped[str] = mapped_column(String(20), default="none")
    recurrence_interval: Mapped[int | None] = mapped_column(Integer, default=1)
    recurrence_until: Mapped[date | None] = mapped_column(Date)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=datetime.utcnow)

    church = relationship("Church", back_populates="events")
    ministry = relationship("Ministry", back_populates="events")
    created_by_user = relationship("User", foreign_keys=[created_by])


class FinancialAccount(Base):
    __tablename__ = "financial_accounts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    church_id: Mapped[str] = mapped_column(ForeignKey("churches.id"), nullable=False)
    ministry_id: Mapped[str | None] = mapped_column(ForeignKey("ministries.id"))
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    bank_name: Mapped[str | None] = mapped_column(String(160))
    account_type: Mapped[str | None] = mapped_column(String(50))
    account_number: Mapped[str | None] = mapped_column(String(80))
    agency: Mapped[str | None] = mapped_column(String(50))
    iban: Mapped[str | None] = mapped_column(String(50))
    swift: Mapped[str | None] = mapped_column(String(30))
    pix_key: Mapped[str | None] = mapped_column(String(160))
    mbway_phone: Mapped[str | None] = mapped_column(String(30))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=datetime.utcnow)

    church = relationship("Church", back_populates="financial_accounts")
    ministry = relationship("Ministry")
    transactions = relationship("Transaction", back_populates="financial_account")


class TransactionCategory(Base):
    __tablename__ = "transaction_categories"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    church_id: Mapped[str] = mapped_column(ForeignKey("churches.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    requires_member: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    church = relationship("Church", back_populates="transaction_categories")
    transactions = relationship("Transaction", back_populates="category")


class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    church_id: Mapped[str] = mapped_column(ForeignKey("churches.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    is_electronic: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    church = relationship("Church", back_populates="payment_methods")
    transactions = relationship("Transaction", back_populates="payment_method")


class Bill(Base):
    __tablename__ = "bills"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    church_id: Mapped[str] = mapped_column(ForeignKey("churches.id"), nullable=False)
    ministry_id: Mapped[str | None] = mapped_column(ForeignKey("ministries.id"))
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    supplier_name: Mapped[str | None] = mapped_column(String(160))
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"))
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=datetime.utcnow)

    church = relationship("Church", back_populates="bills")
    ministry = relationship("Ministry")
    created_by_user = relationship("User", foreign_keys=[created_by])
    transactions = relationship("Transaction", back_populates="bill")


class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    church_id: Mapped[str] = mapped_column(ForeignKey("churches.id"), nullable=False)
    ministry_id: Mapped[str | None] = mapped_column(ForeignKey("ministries.id"))
    category_id: Mapped[str | None] = mapped_column(ForeignKey("transaction_categories.id"))
    payment_method_id: Mapped[str | None] = mapped_column(ForeignKey("payment_methods.id"))
    financial_account_id: Mapped[str | None] = mapped_column(ForeignKey("financial_accounts.id"))
    bill_id: Mapped[str | None] = mapped_column(ForeignKey("bills.id"))
    member_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    receipt_path: Mapped[str | None] = mapped_column(String(255))
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    church = relationship("Church", back_populates="transactions")
    ministry = relationship("Ministry", back_populates="transactions")
    category = relationship("TransactionCategory", back_populates="transactions")
    payment_method = relationship("PaymentMethod", back_populates="transactions")
    financial_account = relationship("FinancialAccount", back_populates="transactions")
    bill = relationship("Bill", back_populates="transactions")
    member = relationship("User", foreign_keys=[member_id])
    created_by_user = relationship("User", foreign_keys=[created_by])


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
