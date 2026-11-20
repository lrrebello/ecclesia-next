from datetime import date, datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.models import (
    Bill,
    Church,
    Donation,
    Event,
    Family,
    Ministry,
    Transaction,
    User,
)
from app.db.base import get_db

router = APIRouter(prefix="/admin", tags=["Administração e Relatórios"])


def get_church_ids(church: Church, db: Session) -> list[str]:
    branches = db.query(Church).filter(Church.parent_id == church.id).all()
    return [church.id] + [branch.id for branch in branches]


def require_admin(user: User, db: Session) -> None:
    from app.core.models import Permission, RolePermission, UserRole

    allowed = (
        db.query(User)
        .join(UserRole, UserRole.user_id == User.id)
        .join(RolePermission, RolePermission.role_id == UserRole.role_id)
        .join(Permission, Permission.id == RolePermission.permission_id)
        .filter(
            User.id == user.id,
            Permission.code == "admin.manage",
        )
        .first()
    )

    if not allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado")


@router.get("/overview")
def overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(current_user, db)

    church = current_user.church

    if not church:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Usuário não vinculado a uma filial")

    church_ids = get_church_ids(church, db)

    members = db.query(func.count(User.id)).filter(User.church_id.in_(church_ids)).scalar() or 0
    pending_members = db.query(func.count(User.id)).filter(
        User.church_id.in_(church_ids),
        User.status == "pending",
    ).scalar() or 0

    families = db.query(func.count(Family.id)).filter(Family.church_id.in_(church_ids)).scalar() or 0
    ministries = db.query(func.count(Ministry.id)).filter(Ministry.church_id.in_(church_ids)).scalar() or 0
    events = db.query(func.count(Event.id)).filter(Event.church_id.in_(church_ids)).scalar() or 0

    transactions = db.query(Transaction).filter(Transaction.church_id.in_(church_ids)).all()

    income = sum(
        transaction.amount
        for transaction in transactions
        if transaction.type == "income"
    )
    expense = sum(
        transaction.amount
        for transaction in transactions
        if transaction.type == "expense"
    )

    donations = db.query(func.coalesce(func.sum(Donation.amount), 0)).filter(
        Donation.church_id.in_(church_ids),
        Donation.is_tax_relevant == True,
    ).scalar() or Decimal("0.00")

    today = date.today()
    next_30_days = today + timedelta(days=30)

    pending_bills = db.query(func.coalesce(func.sum(Bill.amount - Bill.amount_paid), 0)).filter(
        Bill.church_id.in_(church_ids),
        Bill.status != "paid",
        Bill.due_date <= next_30_days,
    ).scalar() or Decimal("0.00")

    overdue_bills = db.query(func.count(Bill.id)).filter(
        Bill.church_id.in_(church_ids),
        Bill.status != "paid",
        Bill.due_date < today,
    ).scalar() or 0

    return {
        "church": {
            "id": church.id,
            "name": church.name,
            "branches": len(church_ids) - 1,
        },
        "members": {
            "total": members,
            "pending": pending_members,
        },
        "families": families,
        "ministries": ministries,
        "events": events,
        "finance": {
            "income": income,
            "expense": expense,
            "balance": income - expense,
            "pending_bills": pending_bills,
            "overdue_bills": overdue_bills,
        },
        "donations": {
            "tax_relevant_total": donations,
        },
    }


@router.get("/branches")
def branch_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(current_user, db)

    church = current_user.church

    if not church:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Usuário não vinculado a uma filial")

    branches = db.query(Church).filter(Church.parent_id == church.id).all()
    report = []

    for branch in [church] + branches:
        members = db.query(func.count(User.id)).filter(User.church_id == branch.id).scalar() or 0
        pending = db.query(func.count(User.id)).filter(
            User.church_id == branch.id,
            User.status == "pending",
        ).scalar() or 0

        families = db.query(func.count(Family.id)).filter(Family.church_id == branch.id).scalar() or 0
        ministries = db.query(func.count(Ministry.id)).filter(Ministry.church_id == branch.id).scalar() or 0
        events = db.query(func.count(Event.id)).filter(Event.church_id == branch.id).scalar() or 0

        transactions = db.query(Transaction).filter(Transaction.church_id == branch.id).all()

        income = sum(
            transaction.amount
            for transaction in transactions
            if transaction.type == "income"
        )
        expense = sum(
            transaction.amount
            for transaction in transactions
            if transaction.type == "expense"
        )

        donations = db.query(func.coalesce(func.sum(Donation.amount), 0)).filter(
            Donation.church_id == branch.id,
            Donation.is_tax_relevant == True,
        ).scalar() or Decimal("0.00")

        report.append({
            "id": branch.id,
            "name": branch.name,
            "type": branch.type,
            "members": members,
            "pending_members": pending,
            "families": families,
            "ministries": ministries,
            "events": events,
            "income": income,
            "expense": expense,
            "balance": income - expense,
            "tax_relevant_donations": donations,
        })

    return {"branches": report}


@router.get("/reports/members")
def members_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(current_user, db)

    church = current_user.church

    if not church:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Usuário não vinculado a uma filial")

    church_ids = get_church_ids(church, db)

    total = db.query(func.count(User.id)).filter(User.church_id.in_(church_ids)).scalar() or 0
    approved = db.query(func.count(User.id)).filter(
        User.church_id.in_(church_ids),
        User.status == "approved",
    ).scalar() or 0
    pending = db.query(func.count(User.id)).filter(
        User.church_id.in_(church_ids),
        User.status == "pending",
    ).scalar() or 0
    rejected = db.query(func.count(User.id)).filter(
        User.church_id.in_(church_ids),
        User.status == "rejected",
    ).scalar() or 0

    return {
        "total": total,
        "approved": approved,
        "pending": pending,
        "rejected": rejected,
    }


@router.get("/reports/finance")
def finance_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(current_user, db)

    church = current_user.church

    if not church:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Usuário não vinculado a uma filial")

    church_ids = get_church_ids(church, db)
    transactions = db.query(Transaction).filter(Transaction.church_id.in_(church_ids)).all()

    monthly = {}

    for transaction in transactions:
        key = transaction.transaction_date.strftime("%Y-%m")

        if key not in monthly:
            monthly[key] = {
                "income": Decimal("0.00"),
                "expense": Decimal("0.00"),
            }

        if transaction.type == "income":
            monthly[key]["income"] += transaction.amount
        else:
            monthly[key]["expense"] += transaction.amount

    report = [
        {
            "month": month,
            "income": values["income"],
            "expense": values["expense"],
            "balance": values["income"] - values["expense"],
        }
        for month, values in sorted(monthly.items())
    ]

    return {"monthly": report}


@router.get("/reports/donations")
def donations_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(current_user, db)

    church = current_user.church

    if not church:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Usuário não vinculado a uma filial")

    church_ids = get_church_ids(church, db)
    donations = db.query(Donation).filter(Donation.church_id.in_(church_ids)).all()

    by_year = {}

    for donation in donations:
        year = donation.donation_date.year

        if year not in by_year:
            by_year[year] = {
                "total": Decimal("0.00"),
                "tax_relevant_total": Decimal("0.00"),
                "count": 0,
            }

        by_year[year]["total"] += donation.amount
        by_year[year]["count"] += 1

        if donation.is_tax_relevant:
            by_year[year]["tax_relevant_total"] += donation.amount

    report = [
        {
            "year": year,
            "total": values["total"],
            "tax_relevant_total": values["tax_relevant_total"],
            "count": values["count"],
        }
        for year, values in sorted(by_year.items())
    ]

    return {"yearly": report}
