from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User

# from app.dependencies.auth import get_current_user
from app.dependencies.roles import required_roles

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard")
async def admin_dashboard(
    request: Request,
    current_user: User = Depends(required_roles(["admin"])),
    db: Session = Depends(get_db),
):
    users = db.query(User).order_by(User.email).all()
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request, "current_user": current_user, "users": users},
    )


@router.post("/users/{user_id}/role")
async def update_user_role(
    request: Request,
    user_id: int,
    new_role: str = Form(...),
    current_user: User = Depends(required_roles(["admin"])),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Validación adicional (opcional)
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes cambiar tu propio rol")

    user.role = new_role
    db.commit()

    # Redirige de vuelta al dashboard
    response = templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "users": db.query(User).all(),
            "success": f"Rol de {user.email} actualizado a {new_role}",
        },
    )
    return response


@router.post("/users/{user_id}/delete")
async def delete_user(
    request: Request,
    user_id: int,
    current_user: User = Depends(required_roles(["admin"])),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Validación para no eliminarse a sí mismo
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")

    db.delete(user)
    db.commit()

    # Redirige de vuelta al dashboard con mensaje de éxito
    users = db.query(User).order_by(User.email).all()
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "users": users,
            "success": f"Usuario {user.email} eliminado correctamente",
        },
    )
