from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import crud, schemas, models
from app.routes.auth import get_current_user
from app.rate_limit import limiter
from app.cloudinary_utils import upload_avatar_file

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/ping")
def ping():
    return {"message": "Contacts OK"}


@router.get("/", response_model=List[schemas.ContactOut])
def list_contacts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_contacts(db, current_user.id)


# ✅ Єдиний правильний POST-ендпоінт
@router.post("/", response_model=schemas.ContactOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def create_contact(
    request: Request,  # 🔹 обов’язково потрібно для slowapi
    contact: schemas.ContactCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_contact(db, contact, current_user.id)


@router.put("/{contact_id}", response_model=schemas.ContactOut)
def update_contact(
    contact_id: int,
    updates: schemas.ContactUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    contact = crud.get_contact(db, contact_id, current_user.id)
    if not contact:
        raise HTTPException(status_code=404, detail="Not found")
    return crud.update_contact(db, contact, updates)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    contact = crud.get_contact(db, contact_id, current_user.id)
    if not contact:
        raise HTTPException(status_code=404, detail="Not found")
    crud.delete_contact(db, contact)
    return None


@router.put("/avatar", status_code=status.HTTP_200_OK)
def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    url = upload_avatar_file(file.file)
    crud.update_user_avatar(db, current_user, url)
    return {"avatar_url": url}
