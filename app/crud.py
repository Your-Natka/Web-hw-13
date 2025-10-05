from sqlalchemy.orm import Session
from typing import List, Optional
from passlib.context import CryptContext
from app import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------- Users ----------
def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: Session, email: str, hashed_password: str, username: Optional[str] = None) -> models.User:
    db_user = models.User(email=email, password=hashed_password[:72], username=username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_password(db: Session, user: models.User, new_password: str) -> models.User:
    user.password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return user

def update_user_avatar(db: Session, user: models.User, avatar_url: str) -> models.User:
    user.avatar_url = avatar_url
    db.commit()
    db.refresh(user)
    return user

def verify_user_email(db: Session, user: models.User) -> models.User:
    user.is_verified = True
    db.commit()
    db.refresh(user)
    return user

# ---------- Contacts ----------
def create_contact(db: Session, contact_in: schemas.ContactCreate, user_id: int) -> models.Contact:
    db_contact = models.Contact(**contact_in.dict(), owner_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contacts(db: Session, user_id: int) -> List[models.Contact]:
    return db.query(models.Contact).filter(models.Contact.owner_id == user_id).all()

def get_contact(db: Session, contact_id: int, user_id: int) -> Optional[models.Contact]:
    return db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.owner_id == user_id
    ).first()

def update_contact(db: Session, contact: models.Contact, updates: schemas.ContactUpdate) -> models.Contact:
    for k, v in updates.dict(exclude_unset=True).items():
        setattr(contact, k, v)
    db.commit()
    db.refresh(contact)
    return contact

def delete_contact(db: Session, contact: models.Contact) -> None:
    db.delete(contact)
    db.commit()