from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class UserRead(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True
        
class Login(BaseModel):
    email: EmailStr
    password: str

