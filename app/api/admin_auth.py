from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.core.security import create_access_token, verify_password
from app.models import AdminUser
from app.schemas.admin import AdminLoginRequest, AdminTokenResponse, AdminUserRead

router = APIRouter(prefix="/admin", tags=["Admin Authentication"])


@router.post("/login", response_model=AdminTokenResponse, summary="Admin user login")
def admin_login(
    login_in: AdminLoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate admin credentials and generate JWT Bearer token.
    """
    admin = (
        db.query(AdminUser)
        .filter(AdminUser.email == login_in.email.strip().lower(), AdminUser.active == True)
        .first()
    )

    if not admin or not verify_password(login_in.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email address or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=admin.id,
        email=admin.email,
        role=admin.role,
    )

    return AdminTokenResponse(
        access_token=access_token,
        token_type="bearer",
        admin_name=admin.name,
        admin_email=admin.email,
    )


@router.post("/logout", summary="Admin logout")
def admin_logout(
    current_admin: AdminUser = Depends(get_current_admin),
):
    """
    Logout active admin session.
    """
    return {
        "status": "success",
        "message": f"Admin '{current_admin.email}' logged out successfully.",
    }


@router.get("/me", response_model=AdminUserRead, summary="Get current admin profile")
def get_admin_me(
    current_admin: AdminUser = Depends(get_current_admin),
):
    """
    Retrieve profile details of currently authenticated admin user.
    """
    return current_admin
