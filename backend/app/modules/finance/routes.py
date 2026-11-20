from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.models import Bill, FinancialAccount, Ministry, PaymentMethod, Transaction, TransactionCategory, User, AuditLog
from app.db.base import get_db

router = APIRouter(prefix="/finance", tags=["Finanças"])


class CategoryInput(BaseModel):
    name: str
    type: str
    requires_member: bool = False


class PaymentMethodInput(BaseModel):
    name: str
    is_electronic: bool = False


class AccountInput(BaseModel):
    name: str
    bank_name: str | None = None
    account_type: str | None = None
    account_number: str | None = None
    agency: str | None = None
    iban: str | None = None
    swift: str | None = None
    pix_key: str | None = None
    mbway_phone: str | None = None
    ministry_id: str | None = None
    notes: str | None = None


class TransactionInput(BaseModel):
    type: str
    amount: Decimal
    description: str | None = None
    transaction_date: date
    category_id: str | None = None
    payment_method_id: str | None = None
    financial_account_id: str | None = None
    ministry_id: str | None = None
    bill_id: str | None = None
    member_id: str | None = None


class BillInput(BaseModel):
    description: str
    supplier_name: str | None = None
    amount: Decimal
    due_date: date
    ministry_id: str | None = None
    notes: str | None = None


def can_manage_finance(user: User, db: Session) -> bool:
    return (
        db.query(User)
        .join(UserRole, UserRole.user_id == User.id)
        .join(RolePermission, RolePermission.role_id == UserRole.role_id)
        .join(Permission, Permission.id == RolePermission.permission_id)
        .filter(
            User.id == user.id,
            Permission.code == "finance.manage",
        )
        .first()
        is not None
    )


from app.core.models import Permission, RolePermission, UserRole


def serialize_transaction(transaction: Transaction) -> dict:
    return {
        "id": transaction.id,
        "type": transaction.type,
        "amount": transaction.amount,
        "description": transaction.description,
        "transaction_date": transaction.transaction_date,
        "category": {
            "id": transaction.category.id,
            "name": transaction.category.name,
        }
        if transaction.category
        else None,
        "payment_method": {
            "id": transaction.payment_method.id,
            "name": transaction.payment_method.name,
        }
        if transaction.payment_method
        else None,
        "financial_account": {
            "id": transaction.financial_account.id,
            "name": transaction.financial_account.name,
        }
        if transaction.financial_account
        else None,
        "ministry": {
            "id": transaction.ministry.id,
            "name": transaction.ministry.name,
        }
        if transaction.ministry
        else None,
        "member": {
            "id": transaction.member.id,
            "name": transaction.member.name,
        }
        if transaction.member
        else None,
        "bill_id": transaction.bill_id,
    }


@router.get("/dashboard")
def dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transactions = db.query(Transaction).filter_by(church_id=current_user.church_id).all()

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

    today = date.today()
    next_30_days = today + timedelta(days=30)

    pending_bills = db.query(func.sum(Bill.amount - Bill.amount_paid)).filter(
        Bill.church_id == current_user.church_id,
        Bill.status != "paid",
        Bill.due_date <= next_30_days,
    ).scalar() or Decimal("0.00")

    overdue_bills = db.query(Bill).filter(
        Bill.church_id == current_user.church_id,
        Bill.status != "paid",
        Bill.due_date < today,
    ).count()

    return {
        "income": income,
        "expense": expense,
        "balance": income - expense,
        "pending_bills": pending_bills,
        "overdue_bills": overdue_bills,
    }


@router.get("/categories")
def list_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    categories = db.query(TransactionCategory).filter_by(
        church_id=current_user.church_id,
        is_active=True,
    ).order_by(TransactionCategory.name).all()

    return {
        "categories": [
            {
                "id": category.id,
                "name": category.name,
                "type": category.type,
                "requires_member": category.requires_member,
            }
            for category in categories
        ]
    }


@router.post("/categories")
def create_category(
    payload: CategoryInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not can_manage_finance(current_user, db):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado")

    if payload.type not in ["income", "expense"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Tipo inválido")

    category = TransactionCategory(
        church_id=current_user.church_id,
        name=payload.name.strip(),
        type=payload.type,
        requires_member=payload.requires_member,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return {
        "id": category.id,
        "name": category.name,
        "type": category.type,
        "requires_member": category.requires_member,
    }


@router.get("/payment-methods")
def list_payment_methods(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    methods = db.query(PaymentMethod).filter_by(
        church_id=current_user.church_id,
        is_active=True,
    ).order_by(PaymentMethod.name).all()

    return {
        "payment_methods": [
            {
                "id": method.id,
                "name": method.name,
                "is_electronic": method.is_electronic,
            }
            for method in methods
        ]
    }


@router.post("/payment-methods")
def create_payment_method(
    payload: PaymentMethodInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not can_manage_finance(current_user, db):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado")

    method = PaymentMethod(
        church_id=current_user.church_id,
        name=payload.name.strip(),
        is_electronic=payload.is_electronic,
    )

    db.add(method)
    db.commit()
    db.refresh(method)

    return {
        "id": method.id,
        "name": method.name,
        "is_electronic": method.is_electronic,
    }


@router.get("/accounts")
def list_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    accounts = db.query(FinancialAccount).filter_by(
        church_id=current_user.church_id,
        is_active=True,
    ).order_by(FinancialAccount.name).all()

    return {
        "accounts": [
            {
                "id": account.id,
                "name": account.name,
                "bank_name": account.bank_name,
                "account_type": account.account_type,
                "ministry_id": account.ministry_id,
            }
            for account in accounts
        ]
    }


@router.post("/accounts")
def create_account(
    payload: AccountInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not can_manage_finance(current_user, db):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado")

    account = FinancialAccount(
        church_id=current_user.church_id,
        ministry_id=payload.ministry_id,
        name=payload.name.strip(),
        bank_name=payload.bank_name,
        account_type=payload.account_type,
        account_number=payload.account_number,
        agency=payload.agency,
        iban=payload.iban,
        swift=payload.swift,
        pix_key=payload.pix_key,
        mbway_phone=payload.mbway_phone,
        notes=payload.notes,
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return {"id": account.id, "name": account.name}


@router.get("/transactions")
def list_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transactions = db.query(Transaction).filter_by(
        church_id=current_user.church_id,
    ).order_by(Transaction.transaction_date.desc()).limit(200).all()

    return {
        "transactions": [serialize_transaction(transaction) for transaction in transactions]
    }


@router.post("/transactions")
def create_transaction(
    payload: TransactionInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not can_manage_finance(current_user, db):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado")

    if payload.type not in ["income", "expense"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Tipo de lançamento inválido")

    if payload.amount <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "O valor deve ser maior que zero")

    category = None
    if payload.category_id:
        category = db.query(TransactionCategory).filter_by(
            id=payload.category_id,
            church_id=current_user.church_id,
        ).first()

        if not category:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Categoria não encontrada")

        if category.requires_member and not payload.member_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Esta categoria exige identificação do membro")

    ministry = None
    if payload.ministry_id:
        ministry = db.query(Ministry).filter_by(
            id=payload.ministry_id,
            church_id=current_user.church_id,
        ).first()

        if not ministry:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Ministério não encontrado")

    member = None
    if payload.member_id:
        member = db.query(User).filter_by(
            id=payload.member_id,
            church_id=current_user.church_id,
        ).first()

        if not member:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Membro não encontrado")

    bill = None
    if payload.bill_id:
        bill = db.query(Bill).filter_by(
            id=payload.bill_id,
            church_id=current_user.church_id,
        ).first()

        if not bill:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Conta a pagar não encontrada")

    transaction = Transaction(
        church_id=current_user.church_id,
        ministry_id=ministry.id if ministry else None,
        category_id=category.id if category else None,
        payment_method_id=payload.payment_method_id,
        financial_account_id=payload.financial_account_id,
        bill_id=bill.id if bill else None,
        member_id=member.id if member else None,
        type=payload.type,
        amount=payload.amount,
        description=payload.description,
        transaction_date=payload.transaction_date,
        created_by=current_user.id,
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    db.add(
        AuditLog(
            user_id=current_user.id,
            church_id=current_user.church_id,
            action="CREATE",
            module="FINANCE",
            description=f"Lançamento criado: {transaction.type} {transaction.amount}",
            new_values={"id": transaction.id, "amount": str(transaction.amount)},
        )
    )
    db.commit()

    return serialize_transaction(transaction)


@router.get("/bills")
def list_bills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bills = db.query(Bill).filter_by(church_id=current_user.church_id).order_by(Bill.due_date).all()

    return {
        "bills": [
            {
                "id": bill.id,
                "description": bill.description,
                "supplier_name": bill.supplier_name,
                "amount": bill.amount,
                "amount_paid": bill.amount_paid,
                "due_date": bill.due_date,
                "status": bill.status,
            }
            for bill in bills
        ]
    }


@router.post("/bills")
def create_bill(
    payload: BillInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not can_manage_finance(current_user, db):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado")

    if payload.amount <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "O valor deve ser maior que zero")

    bill = Bill(
        church_id=current_user.church_id,
        ministry_id=payload.ministry_id,
        description=payload.description.strip(),
        supplier_name=payload.supplier_name,
        amount=payload.amount,
        due_date=payload.due_date,
        notes=payload.notes,
        created_by=current_user.id,
    )

    db.add(bill)
    db.commit()
    db.refresh(bill)

    return {
        "id": bill.id,
        "description": bill.description,
        "amount": bill.amount,
        "due_date": bill.due_date,
        "status": bill.status,
    }
