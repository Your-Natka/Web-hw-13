# Web-hw-13

app/
├── __init__.py
├── main.py                # головний файл (FastAPI app, middleware, routers)
├── database.py            # SQLAlchemy + get_db
├── models.py              # User, Contact
├── schemas.py             # Pydantic схеми
├── crud.py                # логіка бази (users, contacts)
├── mailer.py              # email (verification, reset)
├── cloudinary_utils.py    # завантаження аватарів
├── rate_limit.py          # SlowAPI rate limiter
├── redis_cache.py         # підключення Redis
└── routes/
    ├── auth.py            # маршрути авторизації
    └── contacts.py        # маршрути контактів

Встановлюємо залежності:

pip install -r requirements.txt

Запускаємо Docker сервіси (Postgres + Redis):

docker-compose up -d

Запускаємо FastAPI сервер:

uvicorn app.main:app --reload

Потім відкрий у браузері:
👉 http://127.0.0.1:8000/docs


