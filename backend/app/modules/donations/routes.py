import csv
import io
from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.models import AuditLog, User
from app.db.base import get_db
from app.modules.donations.models import Donation, DonationTaxDeclaration, Donor

router = APIRouter(prefix="/donations", tags=["Donativos e Modelo 25"])


class DonorInput(BaseModel):
    name: str
    tax_id: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None


class DonationInput(BaseModel):
    donor_id: str
    amount: Decimal
    donation_date: str
    donation_type: str = "religious_mecenato"
    receipt_number: str | None = None
    receipt_path: str | None = None
    is_tax_relevant: bool = True
    notes: str | None = None


class DeclarationInput(BaseModel):
    fiscal_year: int


class AddDonationInput(BaseModel):
    donation_id: str


def require_finance_permission(user: User, db: Session) -> None:
    from app.core.models import Permission, RolePermission, UserRole

    allowed = (
        db.query(User)
        .join(UserRole, UserRole.user_id == User.id)
        .join(RolePermission, RolePermission.role_id == UserRole.role_id)
        .join(Permission, Permission.id == RolePermission.permission_id)
        .filter(
            User.id == user.id,
            Permission.code == "finance.manage",
        )
        .first()
    )

    if not allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado")


def serialize_donor(donor: Donor) -> dict:
    return {
        "id": donor.id,
        "name": donor.name,
        "tax_id": donor.tax_id,
        "email": donor.email,
        "phone": donor.phone,
        "address": donor.address,
        "is_active": donor.is_active,
    }


def serialize_donation(donation: Donation) -> dict:
    return {
        "id": donation.id,
        "donor": serialize_donor(donation.donor),
        "amount": donation.amount,
        "donation_date": donation.donation_date,
        "donation_type": donation.donation_type,
        "receipt_number": donation.receipt_number,
        "receipt_path": donation.receipt_path,
        "is_tax_relevant": donation.is_tax_relevant,
        "declaration_id": donation.declaration_id,
        "notes": donation.notes,
    }


def serialize_declaration(declaration: DonationTaxDeclaration) -> dict:
    return {
        "id": declaration.id,
        "church_id": declaration.church_id,
        "fiscal_year": declaration.fiscal_year,
        "status": declaration.status,
        "total_amount": declaration.total_amount,
        "donation_count": declaration.donation_count,
        "submitted_at": declaration.submitted_at,
        "portal_receipt": declaration.portal_receipt,
        "donations": [
            serialize_donation(donation)
            for donation in declaration.donations
        ],
    }


@router.get("/donors")
def list_donors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    donors = db.query(Donor).filter_by(church_id=current_user.church_id).order_by(Donor.name).all()
    return {"donors": [serialize_donor(donor) for donor in donors]}


@router.post("/donors")
def create_donor(
    payload: DonorInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_finance_permission(current_user, db)

    existing = db.query(Donor).filter_by(
        church_id=current_user.church_id,
        tax_id=payload.tax_id,
    ).first()

    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe um doador com este NIF")

    donor = Donor(
        church_id=current_user.church_id,
        name=payload.name.strip(),
        tax_id=payload.tax_id.strip(),
        email=payload.email,
        phone=payload.phone,
        address=payload.address,
    )

    db.add(donor)
    db.commit()
    db.refresh(donor)

    return serialize_donor(donor)


@router.get("")
def list_donations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    donations = db.query(Donation).filter_by(church_id=current_user.church_id).order_by(Donation.donation_date.desc()).all()
    return {"donations": [serialize_donation(donation) for donation in donations]}


@router.post("")
def create_donation(
    payload: DonationInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_finance_permission(current_user, db)

    donor = db.query(Donor).filter_by(
        id=payload.donor_id,
        church_id=current_user.church_id,
    ).first()

    if not donor:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Doador não encontrado")

    if payload.amount <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "O valor do donativo deve ser maior que zero")

    donation = Donation(
        church_id=current_user.church_id,
        donor_id=donor.id,
        amount=payload.amount,
        donation_date=datetime.strptime(payload.donation_date, "%Y-%m-%d").date(),
        donation_type=payload.donation_type,
        receipt_number=payload.receipt_number,
        receipt_path=payload.receipt_path,
        is_tax_relevant=payload.is_tax_relevant,
        notes=payload.notes,
        created_by=current_user.id,
    )

    db.add(donation)
    db.commit()
    db.refresh(donation)

    db.add(
        AuditLog(
            user_id=current_user.id,
            church_id=current_user.church_id,
            action="CREATE",
            module="DONATION",
            description=f"Donativo registado: {donor.name} - {donation.amount}",
            new_values={"id": donation.id, "amount": str(donation.amount)},
        )
    )
    db.commit()

    return serialize_donation(donation)


@router.get("/declarations")
def list_declarations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    declarations = db.query(DonationTaxDeclaration).filter_by(
        church_id=current_user.church_id,
    ).order_by(DonationTaxDeclaration.fiscal_year.desc()).all()

    return {"declarations": [serialize_declaration(declaration) for declaration in declarations]}


@router.post("/declarations")
def create_declaration(
    payload: DeclarationInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_finance_permission(current_user, db)

    existing = db.query(DonationTaxDeclaration).filter_by(
        church_id=current_user.church_id,
        fiscal_year=payload.fiscal_year,
    ).first()

    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe uma declaração para este ano fiscal")

    declaration = DonationTaxDeclaration(
        church_id=current_user.church_id,
        fiscal_year=payload.fiscal_year,
        created_by=current_user.id,
    )

    db.add(declaration)
    db.commit()
    db.refresh(declaration)

    return serialize_declaration(declaration)


@router.post("/declarations/{declaration_id}/donations")
def add_donation_to_declaration(
    declaration_id: str,
    payload: AddDonationInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_finance_permission(current_user, db)

    declaration = db.query(DonationTaxDeclaration).filter_by(
        id=declaration_id,
        church_id=current_user.church_id,
    ).first()

    if not declaration:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Declaração não encontrada")

    if declaration.status != "draft":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "A declaração já foi enviada ou fechada")

    donation = db.query(Donation).filter_by(
        id=payload.donation_id,
        church_id=current_user.church_id,
    ).first()

    if not donation:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Donativo não encontrado")

    if not donation.is_tax_relevant:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Este donativo não é elegível para o Modelo 25")

    if donation.declaration_id:
        raise HTTPException(status.HTTP_409_CONFLICT, "Este donativo já está incluído numa declaração")

    donation.declaration_id = declaration.id
    declaration.donation_count += 1
    declaration.total_amount += donation.amount

    db.commit()
    db.refresh(declaration)

    return serialize_declaration(declaration)


@router.post("/declarations/{declaration_id}/remove-donation")
def remove_donation_from_declaration(
    declaration_id: str,
    payload: AddDonationInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_finance_permission(current_user, db)

    declaration = db.query(DonationTaxDeclaration).filter_by(
        id=declaration_id,
        church_id=current_user.church_id,
    ).first()

    if not declaration:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Declaração não encontrada")

    if declaration.status != "draft":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "A declaração já foi enviada ou fechada")

    donation = db.query(Donation).filter_by(
        id=payload.donation_id,
        church_id=current_user.church_id,
    ).first()

    if not donation or donation.declaration_id != declaration.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Donativo não pertence a esta declaração")

    donation.declaration_id = None
    declaration.donation_count -= 1
    declaration.total_amount -= donation.amount

    db.commit()
    db.refresh(declaration)

    return serialize_declaration(declaration)


@router.get("/declarations/{declaration_id}/export")
def export_declaration(
    declaration_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_finance_permission(current_user, db)

    declaration = db.query(DonationTaxDeclaration).filter_by(
        id=declaration_id,
        church_id=current_user.church_id,
    ).first()

    if not declaration:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Declaração não encontrada")

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow([
        "ANO_FISCAL",
        "NIF_DOADOR",
        "NOME_DOADOR",
        "VALOR_DONATIVO",
        "DATA_DONATIVO",
        "TIPO_DONATIVO",
        "NUMERO_RECIBO",
    ])

    for donation in declaration.donations:
        writer.writerow([
            declaration.fiscal_year,
            donation.donor.tax_id,
            donation.donor.name,
            f"{donation.amount:.2f}".replace(".", ","),
            donation.donation_date.isoformat(),
            donation.donation_type,
            donation.receipt_number or "",
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=modelo25-{declaration.fiscal_year}.csv"
        },
    )


@router.post("/declarations/{declaration_id}/submit")
def mark_declaration_submitted(
    declaration_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_finance_permission(current_user, db)

    declaration = db.query(DonationTaxDeclaration).filter_by(
        id=declaration_id,
        church_id=current_user.church_id,
    ).first()

    if not declaration:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Declaração não encontrada")

    if declaration.status != "draft":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "A declaração já foi enviada")

    if declaration.donation_count == 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "A declaração não possui donativos")

    declaration.status = "submitted"
    declaration.submitted_at = datetime.utcnow()
    declaration.submitted_by = current_user.id

    db.commit()

    db.add(
        AuditLog(
            user_id=current_user.id,
            church_id=current_user.church_id,
            action="SUBMIT",
            module="MODEL_25",
            description=f"Declaração Modelo 25 marcada como enviada: {declaration.fiscal_year}",
            new_values={
                "id": declaration.id,
                "fiscal_year": declaration.fiscal_year,
                "total_amount": str(declaration.total_amount),
            },
        )
    )
    db.commit()

    return serialize_declaration(declaration)
