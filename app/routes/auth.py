from dotenv import load_dotenv
import os
from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserOut, UserLogin
from app.models.user import User
from app.database import get_db
from app.utils.auth import hash_password
from jose import jwt
from datetime import datetime, timedelta
from app.utils.auth import verify_password, create_access_token
from app.dependencies.auth import get_db
from urllib.parse import urlencode
from app.dependencies.roles import required_roles

load_dotenv()
router = APIRouter(prefix="/auth", tags=["Auth"])
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


@router.post("/signup")
async def signup(
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form("user"),
    db: Session = Depends(get_db),
):
    # Verificar si el usuario ya existe
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        error_msg = urlencode({"error": "El email ya está registrado"})
        return RedirectResponse(f"/signup?{error_msg}", status_code=303)

    # Crear nuevo usuario (CORRECCIÓN AQUÍ)
    hashed_password = hash_password(
        password
    )  # Usar la variable 'password' del formulario
    new_user = User(email=email, hashed_password=hashed_password, role=role)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    success_msg = urlencode({"success": "Registro exitoso! Por favor inicia sesión"})
    return RedirectResponse(f"/?{success_msg}", status_code=303)


@router.post("/login")
async def login(
    username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == username).first()
    if not user or not verify_password(password, user.hashed_password):
        error_msg = urlencode({"error": "Credenciales incorrectas"})
        return RedirectResponse(f"/?{error_msg}", status_code=303)

    access_token = create_access_token(data={"sub": user.email})
    response = RedirectResponse("/welcome", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}")
    return response


@router.get("/admin/users")
async def list_users(
    admin: User = Depends(required_roles(["admin"])), db: Session = Depends(get_db)
):
    return db.query(User).all()
