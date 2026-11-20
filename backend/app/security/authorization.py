from fastapi import Depends, HTTPException, status
from app.db.base import get_db
from app.core.models import User, UserRole, RolePermission, Permission
from sqlalchemy.orm import Session

def current_user(db: Session = Depends(get_db)) -> User | None:
    return None

def authorize(permission_code: str, scope_type: str | None = None, scope_id: str | None = None):
    def dependency(user=Depends(current_user), db: Session = Depends(get_db)):
        if user is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Não autenticado")
        query = (
            db.query(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .filter(UserRole.user_id == user.id, Permission.code == permission_code)
        )
        if scope_type:
            query = query.filter(UserRole.scope_type == scope_type)
        if scope_id:
            query = query.filter(UserRole.scope_id == scope_id)
        if not query.first():
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado")
        return True
    return dependency
