from pydantic import BaseModel, Field, EmailStr


class UserInput(BaseModel):
    first_name: str = Field(...)
    second_name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    description: str = Field(...)


class UserLogin(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)
