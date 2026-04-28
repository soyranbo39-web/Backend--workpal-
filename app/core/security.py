import os
from datatime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError


SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
credentials_exec = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def raise_exception_token ():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
def raise_frobidden():
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permisos para acceder a este recurso",
    )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#falta implementar 
def verify_token():
    pass 

def decode_token(token: str)-> dict:
    playload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
    return playload

def get_current_user(token: str = Depends(oauth2_scheme)):

    try:
        payload = decode_token(token)
        sub = Optional[str] = payload.get("sub")
        username:Optional[str] = payload.get("username")

        if not sub or not username:
            raise credentials_exec
        
        return {"sub": sub, "email": sub,  "username": username}
    
    except ExpiredSignatureError:
        raise_exception_token()
    
    except InvalidTokenError:
        raise credentials_exec


   