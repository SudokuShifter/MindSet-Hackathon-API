import re

from fastapi import Form
from pydantic import BaseModel, EmailStr, field_validator


class LoginForm(BaseModel):
    email: EmailStr = Form()
    password: str = Form()


class RegisterForm(LoginForm):
    first_name: str = Form()
    second_name: str = Form()
    description: str = Form()

    @field_validator("password", mode="before")
    def validate_password(cls, value: str) -> str:
        min_length = 8

        if len(value) < min_length:
            raise ValueError("Password must be at least 8 characters long")

        if (
            not any(c.isupper() for c in value)
            or not any(c.islower() for c in value)
            or not any(c.isdigit() for c in value)
            or not any(not c.isalnum() for c in value)
        ):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, one digit, and one special character."
            )
        return value

    @field_validator("first_name", "second_name", mode="before")
    def validate_name_and_surname(cls, value: str) -> str:
        if not re.fullmatch(r"[A-Za-zА-Яа-я]+", value):
            raise ValueError("Value must contain only letters")
        return value
