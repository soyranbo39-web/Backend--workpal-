import os
import shutil
import uuid

from fastapi import HTTPException, UploadFile, status

MEDIA_DIR= "app/media"
ALLOW_MINE =["image/jpeg","image/png"]
MAX_MB =int(os.getenv("mAX_UPLOAD_MB","10"))
CHUNKS = 1024 * 1024



def ensure_media_dir():
    os.makedirs(MEDIA_DIR, exist_ok=True)

async def save_uploaded_image(file:UploadFile)-> dict:
    
    if file.content_type not in ALLOW_MINE:
        raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Formato no soportado"
)
    ensure_media_dir()
    ext=os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(MEDIA_DIR,filename)
    
 
    with open(file_path,"wb") as buffer:
        shutil.copyfileobj(file.file, buffer, length=CHUNKS)
    size = os.path.getsize(file_path)
    if size > MAX_MB * 1024 * 1024:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Archivo demasiado grande (maximo {MAX_MB}MB)"
            
        )
    

    return {
    "filename": file.filename,
    "content_type": file.content_type,
    "url":f"/media/{filename}",
  
}