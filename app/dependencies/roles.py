from fastapi import Depends, HTTPException, status
from .auth import get_current_user
from app.models.user import User


def required_roles(required_roles: list[str]):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operación no permitida para tu rol",
            )
        return current_user

    return role_checker
