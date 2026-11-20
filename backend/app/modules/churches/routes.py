from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.models import Church, User
from app.db.base import get_db

router = APIRouter(prefix="/churches", tags=["Igrejas e filiais"])


class ChurchInput(BaseModel):
    name: str
    slug: str
    type: str = "branch"
    parent_id: str | None = None
    country: str | None = None
    currency_code: str = "EUR"
    is_main: bool = False


def serialize_church(church: Church) -> dict:
    return {
        "id": church.id,
        "name": church.name,
        "slug": church.slug,
        "type": church.type,
        "parent_id": church.parent_id,
        "country": church.country,
        "currency_code": church.currency_code,
        "is_main": church.is_main,
        "is_active": church.is_active,
    }


@router.get("/public")
def list_public_churches(db: Session = Depends(get_db)):
    main_churches = db.query(Church).filter_by(
        is_active=True,
        is_main=True,
    ).order_by(Church.name).all()

    return {
        "churches": [
            {
                **serialize_church(church),
                "branches": [
                    serialize_church(branch)
                    for branch in church.branches
                    if branch.is_active
                ],
            }
            for church in main_churches
        ]
    }


@router.get("")
def list_churches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.church_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Usuário não vinculado a uma igreja")

    church = db.query(Church).filter_by(id=current_user.church_id).first()
    if not church:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Igreja não encontrada")

    parent_id = church.parent_id or church.id
    churches = db.query(Church).filter(
        Church.is_active == True,
        Church.id == parent_id | Church.parent_id == parent_id,
    ).order_by(Church.name).all()

    return {"churches": [serialize_church(church) for church in churches]}


@router.post("")
def create_church(
    payload: ChurchInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if db.query(Church).filter_by(slug=payload.slug).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe uma igreja ou filial com este identificador")

    if payload.parent_id:
        parent = db.query(Church).filter_by(id=payload.parent_id).first()
        if not parent:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Igreja-mãe não encontrada")

    church = Church(
        name=payload.name.strip(),
        slug=payload.slug.lower().strip(),
        type=payload.type,
        parent_id=payload.parent_id,
        country=payload.country,
        currency_code=payload.currency_code,
        is_main=payload.is_main,
    )

    db.add(church)
    db.commit()
    db.refresh(church)

    return serialize_church(church)
