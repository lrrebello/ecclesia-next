from app.db.base import SessionLocal
from app.core.models import Church, Permission, Role, RolePermission, User, UserRole
from app.security.password import hash_password


def get_or_create_permission(db, code: str, description: str):
    permission = db.query(Permission).filter_by(code=code).first()

    if not permission:
        permission = Permission(code=code, description=description)
        db.add(permission)
        db.flush()

    return permission


def get_or_create_role(db, name: str, description: str, is_system: bool = False):
    role = db.query(Role).filter_by(name=name, church_id=None).first()

    if not role:
        role = Role(name=name, description=description, is_system=is_system)
        db.add(role)
        db.flush()

    return role


def get_or_create_church(db, name: str, slug: str, church_type: str, is_main: bool, parent=None):
    church = db.query(Church).filter_by(slug=slug).first()

    if not church:
        church = Church(
            name=name,
            slug=slug,
            type=church_type,
            is_main=is_main,
            parent_id=parent.id if parent else None,
        )
        db.add(church)
        db.flush()

    return church


def get_or_create_user(db, email: str, name: str, password: str, church_id: str, status: str = "pending"):
    user = db.query(User).filter_by(email=email).first()

    if not user:
        user = User(
            email=email,
            name=name,
            password_hash=hash_password(password),
            church_id=church_id,
            status=status,
            is_email_verified=True,
        )
        db.add(user)
        db.flush()

    return user


def run_seed():
    db = SessionLocal()

    try:
        main_church = get_or_create_church(
            db,
            name="Igreja Central",
            slug="igreja-central",
            church_type="main",
            is_main=True,
        )

        branch_one = get_or_create_church(
            db,
            name="Filial Norte",
            slug="filial-norte",
            church_type="branch",
            is_main=False,
            parent=main_church,
        )

        branch_two = get_or_create_church(
            db,
            name="Filial Sul",
            slug="filial-sul",
            church_type="branch",
            is_main=False,
            parent=main_church,
        )

        permissions = {
            "admin.manage": "Permite acessar administração e relatórios consolidados",
            "finance.manage": "Permite gerenciar finanças da filial",
            "member.approve": "Permite aprovar ou rejeitar membros",
            "ministry.manage": "Permite gerenciar ministérios",
            "event.manage": "Permite gerenciar eventos",
            "media.manage": "Permite gerenciar mídia e devocionais",
            "study.manage": "Permite gerenciar estudos e quizzes",
        }

        permission_map = {}

        for code, description in permissions.items():
            permission_map[code] = get_or_create_permission(db, code, description)

        admin_role = get_or_create_role(
            db,
            name="Administrador Global",
            description="Acesso administrativo completo",
            is_system=True,
        )

        member_role = get_or_create_role(
            db,
            name="Membro",
            description="Acesso básico de membro",
            is_system=True,
        )

        for permission in permission_map.values():
            existing = db.query(RolePermission).filter_by(
                role_id=admin_role.id,
                permission_id=permission.id,
            ).first()

            if not existing:
                db.add(RolePermission(role_id=admin_role.id, permission_id=permission.id))

        admin_user = get_or_create_user(
            db,
            email="admin@teste.com",
            name="Administrador Teste",
            password="Teste@1234",
            church_id=main_church.id,
            status="approved",
        )

        existing_admin_role = db.query(UserRole).filter_by(
            user_id=admin_user.id,
            role_id=admin_role.id,
        ).first()

        if not existing_admin_role:
            db.add(UserRole(user_id=admin_user.id, role_id=admin_role.id))

        member_one = get_or_create_user(
            db,
            email="membro.norte@teste.com",
            name="Membro Norte",
            password="Membro@1234",
            church_id=branch_one.id,
            status="pending",
        )

        member_two = get_or_create_user(
            db,
            email="membro.sul@teste.com",
            name="Membro Sul",
            password="Membro@1234",
            church_id=branch_two.id,
            status="pending",
        )

        for member in [member_one, member_two]:
            existing_member_role = db.query(UserRole).filter_by(
                user_id=member.id,
                role_id=member_role.id,
            ).first()

            if not existing_member_role:
                db.add(UserRole(user_id=member.id, role_id=member_role.id))

        db.commit()

        print("Seed concluído.")
        print("Admin: admin@teste.com / Teste@1234")
        print("Membro Norte: membro.norte@teste.com / Membro@1234")
        print("Membro Sul: membro.sul@teste.com / Membro@1234")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
