from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- USERS ---
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user_in: schemas.UserCreate):
    hashed = pwd_context.hash(user_in.password)
    db_user = models.User(email=user_in.email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- ITEMS ---
def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()


def get_items(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Item).offset(skip).limit(limit).all()


# --- CONTACTS ---
def create_contact(db: Session, contact: schemas.ContactCreate):
    db_contact = models.Contact(**contact.dict())
    db.add(db_contact)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Phone or email already exists")
    db.refresh(db_contact)
    return db_contact


def get_contacts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Contact).offset(skip).limit(limit).all()


def get_contact(db: Session, contact_id: int):
    return db.query(models.Contact).filter(models.Contact.id == contact_id).first()


# --- UPDATE CONTACT ---
def update_contact_full(db: Session, contact_id: int, contact_in: schemas.ContactCreate):
    """PUT — повне оновлення (усі поля обов’язкові)"""
    db_contact = get_contact(db, contact_id)
    if not db_contact:
        return None
    for key, value in contact_in.dict().items():
        setattr(db_contact, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Phone or email already exists")
    db.refresh(db_contact)
    return db_contact


def update_contact_partial(db: Session, contact_id: int, contact_in: schemas.ContactUpdate):
    """PATCH — часткове оновлення (тільки передані поля)"""
    db_contact = get_contact(db, contact_id)
    if not db_contact:
        return None
    for key, value in contact_in.dict(exclude_unset=True).items():
        setattr(db_contact, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Phone or email already exists")
    db.refresh(db_contact)
    return db_contact


def delete_contact(db: Session, contact_id: int):
    db_contact = get_contact(db, contact_id)
    if not db_contact:
        return False
    db.delete(db_contact)
    db.commit()
    return True


def contacts_with_birthdays_next_days(db: Session, days: int = 7):
    today = date.today()
    end_date = today + timedelta(days=days)

    contacts = db.query(models.Contact).all()
    result = []

    for contact in contacts:
        if contact.birthday:
            birthday_this_year = contact.birthday.replace(year=today.year)
            if today <= birthday_this_year <= end_date:
                result.append(contact)

    return result

