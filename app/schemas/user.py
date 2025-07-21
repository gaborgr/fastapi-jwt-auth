from pydantic import BaseModel, EmailStr, field_validator
import re


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    def validate_email(cls, email):
        # Regex para validar emails (ej: user@example.com)
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, email):
            raise ValueError("¡Email no válido! 🚨")
        return email


class UserOut(BaseModel):
    id: int
    email: EmailStr
    # No incluir password por seguridad!


class UserLogin(BaseModel):
    email: str
    password: str
