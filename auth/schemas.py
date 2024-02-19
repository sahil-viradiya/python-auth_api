from pydantic import BaseModel, EmailStr


class createUser(BaseModel):
    name: str
    email: EmailStr
    password: str


class loginUser(BaseModel):
    email: EmailStr
    password: str
