import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, Date, ForeignKey, Text, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def uuid_default():
    return str(uuid.uuid4())


class Donor(Base):
    __tablename__ = "donors"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    church_id: Mapped[str] = mapped_column(ForeignKey("churches.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    tax_id: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=datetime.utcnow)

    donations = relationship("Donation", back_populates="donor")


class Donation(Base):
    __tablename__ = "donations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    church_id: Mapped[str] = mapped_column(ForeignKey("churches.id"), nullable=False)
    donor_id: Mapped[str] = mapped_column(ForeignKey("donors.id"), nullable=False)
    transaction_id: Mapped[str | None] = mapped_column(ForeignKey("transactions.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    donation_date: Mapped[date] = mapped_column(Date, nullable=False)
    donation_type: Mapped[str] = mapped_column(String(50), default="religious_mecenato")
    receipt_number: Mapped[str | None] = mapped_column(String(80))
    receipt_path: Mapped[str | None] = mapped_column(String(255))
    is_tax_relevant: Mapped[bool] = mapped_column(Boolean, default=True)
    declaration_id: Mapped[str | None] = mapped_column(ForeignKey("donation_tax_declarations.id"))
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=datetime.utcnow)

    donor = relationship("Donor", back_populates="donations")
    declaration = relationship(
        "DonationTaxDeclaration",
        back_populates="donations",
        foreign_keys=[declaration_id],
    )


class DonationTaxDeclaration(Base):
    __tablename__ = "donation_tax_declarations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    church_id: Mapped[str] = mapped_column(ForeignKey("churches.id"), nullable=False)
    fiscal_year: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="draft")
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"))
    donation_count: Mapped[int] = mapped_column(default=0)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime)
    submitted_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    portal_receipt: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=datetime.utcnow)

    donations = relationship(
        "Donation",
        back_populates="declaration",
        foreign_keys=[Donation.declaration_id],
    )


class TaxDeclarationFile(Base):
    __tablename__ = "tax_declaration_files"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    declaration_id: Mapped[str] = mapped_column(ForeignKey("donation_tax_declarations.id"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    file_format: Mapped[str] = mapped_column(String(20), default="csv")
    generated_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    declaration = relationship("DonationTaxDeclaration", backref="files")
