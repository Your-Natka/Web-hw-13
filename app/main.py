from fastapi import FastAPI, Depends, HTTPException, Request, status, File, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.security import OAuth2PasswordRequestForm
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.rate_limit import limiter
from jose import jwt, JWTError
from app import models, schemas, crud
from app.database import engine, SessionLocal, Base 
from app import auth
from slowapi.util import get_remote_address

app = FastAPI(title="Contacts API")
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # або ["*"] для тестування
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Створюємо таблиці (тільки один раз)
Base.metadata.create_all(bind=engine)

# Dependency для сесії
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception:
        raise HTTPException(status_code=500, detail="Error connecting to the database")

# Регистрация користувача
@app.post("/auth/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    user = crud.create_user(db, user_in)
    return user

# Логін -> повертає access + refresh
@app.post("/auth/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)  # username == email
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")

    access_token = auth.create_access_token(subject=user.id)
    refresh_token = auth.create_refresh_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


# Refresh access token
@app.post("/auth/refresh", response_model=schemas.Token)
def refresh_token(payload: dict, db: Session = Depends(get_db)):
    """
    Очікує JSON: {"refresh_token": "..."}
    """
    refresh = payload.get("refresh_token")
    if not refresh:
        raise HTTPException(status_code=400, detail="refresh_token required")
    try:
        decoded = auth.jwt.decode(refresh, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        user_id = int(decoded.get("sub"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    new_access = auth.create_access_token(subject=user.id)
    new_refresh = auth.create_refresh_token(subject=user.id)
    return {"access_token": new_access, "token_type": "bearer", "refresh_token": new_refresh}

@app.get("/auth/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("action") != "verify":
            raise HTTPException(status_code=400, detail="Invalid token")
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404)
    user.is_verified = True
    db.commit()
    return {"message": "Email verified"}

@app.post("/auth/reset/confirm")
def reset_confirm(token: str, new_password: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("action") != "reset":
            raise HTTPException(status_code=400)
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404)
    user.hashed_password = crud.get_password_hash(new_password)
    db.commit()
    # optional: delete redis cache
    redis_cache.delete_cached_user(user.id)
    return {"message": "Password updated"}

@app.post("/users/me/avatar", response_model=schemas.UserOut)
def upload_avatar(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    url = cloudinary_utils.upload_avatar(file)
    current_user.avatar_url = url
    db.commit()
    db.refresh(current_user)
    return current_user

# Захищені CRUD операції для контактів
# CONTACTS CRUD
# CREATE
@app.post("/contacts/", response_model=schemas.ContactOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute", key_func=lambda request: request.state.user_key)
def create_contact(
    contact: schemas.ContactCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return crud.create_contact(db, contact, owner_id=current_user.id)


@app.get("/contacts/{contact_id}", response_model=schemas.ContactOut)
def read_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    contact = crud.get_contact(db, contact_id)
    if not contact or contact.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@app.get("/contacts/", response_model=list[schemas.ContactOut])
def read_contacts(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return crud.get_contacts(db, owner_id=current_user.id, skip=skip, limit=limit)

# UPDATE (PUT — повне оновлення)
@app.put("/contacts/{contact_id}", response_model=schemas.ContactOut)
def update_contact(
    contact_id: int,
    contact: schemas.ContactCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    res = crud.update_contact_full(db, contact_id, contact, owner_id=current_user.id)
    if not res:
        raise HTTPException(status_code=404, detail="Contact not found or unauthorized")
    return res

# PATCH (часткове оновлення)
@app.patch("/contacts/{contact_id}", response_model=schemas.ContactOut)
def update_contact_partial(
    contact_id: int,
    contact: schemas.ContactUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    res = crud.update_contact_partial(db, contact_id, contact, owner_id=current_user.id)
    if not res:
        raise HTTPException(status_code=404, detail="Contact not found or unauthorized")
    return res

# DELETE
@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    ok = crud.delete_contact(db, contact_id, owner_id=current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Contact not found or unauthorized")
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})


# Validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "message": "Validation Error",
            "errors": exc.errors(),
            "body": str(exc.body)  # перетворюємо bytes у str
        },
    )
    
# обробка помилок
@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request, exc):
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})