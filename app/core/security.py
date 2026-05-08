
from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.api.v1.auth.repository import UserRepository
from app.core.config import settings
from app.core.db import get_db
from app.Models.Users import User

password_hash = PasswordHash.recommended()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
credentials_exec=HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="no autenticado",
    headers= {"WWW-Authenticate":"Bearer"}

)


def raise_exception_token():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expirado",
        headers= {"WWW-Authenticate":"Bearer"}
        
    )
    
def raise_frobidden():
    raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="no tienes los permisos suficientes",
    headers= {"WWW-Authenticate":"Bearer"}
)
    
def invalid_credentials():
    raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="credenciales invalidas",
    headers= {"WWW-Authenticate":"Bearer"}
)
def hash_password(password:str)-> str:
    return password_hash.hash(password)

def verify_password(password:str, hashed_password:str)-> bool:
    return password_hash.verify(password, hashed_password)


# def create_access_token(data:dict, expires_delta: Optional[timedelta]=None):
#     to_encode= data.copy()
#     espire= datetime.now(tz=timezone.utc) + (expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp":espire})
#     token=jwt.encode(payload=to_encode,key=settings.JWT_SECRET_KEY,algorithm=settings.JWT_ALGORITHM)
#     return token

def create_access_token(sub : str, minutes: int | None = None )-> str:
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=minutes or settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
    return jwt.encode({"sub": sub, "exp": expire}, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def verify_token():

    pass

def decode_token(token:str)-> dict:
    payload = jwt.decode(jwt=token, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    return payload


async def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    token: str = Depends(oauth2_scheme),
) -> User:
    try:
        payload = decode_token(token)
        sub: Optional[str] = payload.get("sub") 
     
        
        if not sub:
            raise credentials_exec

        user_id = int (sub)

    except ExpiredSignatureError:
        raise_exception_token()
    except InvalidTokenError:
        raise credentials_exec
    except jwt.PyJWTError:
        raise invalid_credentials()
    
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise invalid_credentials()
    return user


def requiere_role(min_role : Literal["user","editor", "admin"]):
    order = {"user": 0, "editor": 1, "admin": 2}
    
    def evaluation(user : Annotated[User, Depends(get_current_user)])-> User:
        if order[user.role] < order[min_role]:
            raise raise_frobidden()
        return user
    return evaluation 


async def auth2_token (form: Annotated[OAuth2PasswordRequestForm, Depends()], db :Annotated[Session,Depends(get_db)]):
    repository = UserRepository(db)
    user = repository.get_by_email(form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise invalid_credentials()
    token = create_access_token(sub=str(user.id))
    return {"access_token":token, "token_tupe":"bearer"}
    
    

requere_user = requiere_role("user")
requere_editor = requiere_role("editor")
requere_admin = requiere_role("admin") 

 