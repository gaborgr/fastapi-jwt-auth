from fastapi import Depends, HTTPException, status, Request  # Añade Request
from jose import JWTError, jwt
from dotenv import load_dotenv
from app.database import get_db
from app.models.user import User
from sqlalchemy.orm import Session
import os


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


async def get_current_user(
    request: Request,  # Añadimos el request para acceder a cookies
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Obtenemos el token de las cookies
    token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception

    try:
        # Remueve "Bearer " si está presente
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
