from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.models import User, UserRole, RolePermission, Permission
from app.db.base import get_db


def authorize(permission_code: str, scope_type: str | None = None, scope_id: str | None = None):
    def dependency(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> bool:
        query = (
            db.query(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .filter(UserRole.user_id == user.id)
            .filter(Permission.code == permission_code)
        )

        if scope_type:
            query = query.filter(UserRole.scope_type == scope_type)

        if scope_id:
            query = query.filter(UserRole.scope_id == scope_id)

        if not query.first():
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado")

        return True

    return dependency
