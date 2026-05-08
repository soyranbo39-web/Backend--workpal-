
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED

from app.api.v1.auth.repository import UserRepository
from app.core.db import get_db
from app.core.security import (
    auth2_token,
    create_access_token,
    get_current_user,
    hash_password,
    requere_admin,
    verify_password,
)
from app.Models.Users import User

from .schemas import Role, RoleUpdate, TokenResponse, UserCreate, UserLogin, UserPublic

router=APIRouter(prefix="/auth",tags=["auth"])

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db :Annotated[Session, Depends(get_db)] ):
    repository =UserRepository(db)
    if repository.get_by_email(payload.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email ya esta registrado")
    user= repository.create(
        email= payload.email,
        hashed_password= hash_password(payload.password),
        full_name=payload.full_name
        
        )
    db.commit()
    db.refresh(user)
    return UserPublic.model_validate(user)
    
 

@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db : Annotated[Session, Depends(get_db)]):
    repository = UserRepository(db)
    user = repository.get_by_email(payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code= HTTP_401_UNAUTHORIZED,
            detail= "credenciales invalidas"
        )
    token = create_access_token(sub=str(user.id))
    return TokenResponse(access_token=token,user=UserPublic.model_validate(user))
    
    


@router.get("/me",response_model=UserPublic)
async def read_me(
    current: Annotated[User, Depends(get_current_user)]
    ):
    return UserPublic.model_validate(current)
    
@router.put("/role/{user_id}", response_model=UserPublic)
def set_role(
    user_id: Annotated[int, Path(ge=1)],
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[User, Depends(requere_admin)],
    payload: RoleUpdate,
             ):
    repossitory = UserRepository(db)
    user = repossitory.gte(user_id)
    if not user: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    updated = repossitory.set_role(user, payload.role)
    db.commit()
    db.refresh(user)
    return UserPublic.model_validate(updated)
    
@router.post("/token")
async def token_endpoint(response =Depends(auth2_token) ):
    return response