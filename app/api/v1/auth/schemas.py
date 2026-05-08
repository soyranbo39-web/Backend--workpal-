from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

Role = Literal["admin","user","editor"]

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional [str] = None
    model_config = ConfigDict(from_attributes=True)
  
class UserPublic(UserBase):
    id : int
    role: Role
    is_active: bool  
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str="bearer"
    user : UserPublic

class TokenData(BaseModel):
    username: str 
    sub: str 
    
    
class UserCreate(UserBase):
    email: str
    password: str = Field(..., min_length=6, max_length=255, description="Contraseña")
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str 
    
class RoleUpdate(BaseModel):
    role: Role
    
    

