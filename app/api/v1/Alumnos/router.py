
from typing import Optional, Annotated
from typing import cast

from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session
from .schemas import AlumnoCreate, AlumnoResponse
from app.core.security import get_current_user
from app.api.repository import PostRepository
from app.core.db import get_db
from app.services.file_storage import save_uploaded_image





router = APIRouter(
    prefix="/alumnos",
    tags=["alumnos"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=AlumnoResponse)
async def create_alumno(
    alumno: Annotated[AlumnoCreate, Depends(AlumnoCreate.as_form)],
    imagen: Annotated[Optional[UploadFile], File()] = None,
    db: Annotated[Session, Depends(get_db)] = None,
    user: Annotated[dict, Depends(get_current_user)] = None,
):
    repo = PostRepository(db)
    saved : Optional[dict[str, str]] = None
    try:
        if imagen is not None:
            saved= cast(dict [str, str], await save_uploaded_image(imagen))
        
        imagen_url : str = saved["url"] if saved is not None else ""
        if alumno.name is None : 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El campo 'name' es obligatorio")
        
        created_post = repo.create_alumno(
            AlumnoCreate(
                name=alumno.name,
                last_name=alumno.last_name,
                carrera=alumno.carrera,
                imagen_url=imagen_url
            )
        )
        db.commit()
        db.refresh(created_post)
        return created_post
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Alumno con el mismo ID ya existe")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el alumno")
        
            
