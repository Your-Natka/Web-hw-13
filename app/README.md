📌 Web-hw-12 — FastAPI Contacts API
🚀 Опис

Цей проєкт реалізує REST API для роботи з користувачами та контактами на основі FastAPI.
Є підтримка реєстрації, аутентифікації (JWT access/refresh токени), CRUD для контактів.
Кожен користувач має доступ лише до власних контактів.

⚙️ Стек технологій

FastAPI

Uvicorn

SQLAlchemy

Passlib (bcrypt)

Python-JOSE

📂 Структура проєкту
Web-hw-12/
│── app/
│   ├── main.py         # Точка входу
│   ├── database.py     # Підключення до БД
│   ├── models.py       # SQLAlchemy моделі (User, Contact)
│   ├── schemas.py      # Pydantic-схеми
│   ├── crud.py         # CRUD-операції
│   ├── auth.py         # JWT логіка (access + refresh токени)
│   └── utils.py        # Хелпери (хешування паролів і т.д.)
│
│── README.md           # Документація
│── requirements.txt    # Залежності

📦 Встановлення

Клонувати репозиторій:

git clone https://github.com/your-username/Web-hw-12.git
cd Web-hw-12


Створити та активувати віртуальне середовище:

python3 -m venv venv
source venv/bin/activate   # для Mac/Linux
venv\Scripts\activate      # для Windows


Встановити залежності:

pip install -r requirements.txt


⚠️ Якщо виникне помилка з bcrypt, встановіть сумісну версію:

pip install "bcrypt<4.0.0"

▶️ Запуск сервера
uvicorn app.main:app --reload


API буде доступне за адресою:
👉 http://127.0.0.1:8000/docs
 (Swagger UI)

🔑 Авторизація

Використовується JWT (Bearer Token).

Access-токен живе 15 хвилин, refresh-токен — довше (наприклад, 7 днів).

Основні ендпоінти
Auth

POST /auth/register — реєстрація

POST /auth/token — логін (отримання токенів)

POST /auth/refresh — оновлення токена

Contacts (захищені)

GET /contacts/ — список контактів

POST /contacts/ — створення контакту

GET /contacts/{contact_id} — отримати контакт

PUT /contacts/{contact_id} — оновити контакт

DELETE /contacts/{contact_id} — видалити контакт

🧪 Тестування

Зареєструвати користувача через /auth/register.

Залогінитись через /auth/token, отримати access_token.

У Swagger натиснути Authorize → вставити Bearer <access_token>.

Виконувати CRUD-запити для контактів.

📌 Приклади запитів
🔐 Авторизація
1. Реєстрація користувача

POST /auth/register

{
  "email": "test@example.com",
  "password": "secret123",
  "full_name": "Test User"
}

2. Логін

POST /auth/token

{
  "email": "test@example.com",
  "password": "secret123"
}


👉 Відповідь:

{
  "access_token": "eyJhbGciOiJIUzI1...",
  "token_type": "bearer",
  "refresh_token": "eyJhbGciOiJIUzI1..."
}

3. Оновлення токена

POST /auth/refresh

{
  "refresh_token": "eyJhbGciOiJIUzI1..."
}

📇 Контакти (потребує Bearer Token)
1. Створити контакт

POST /contacts/
Headers:

Authorization: Bearer <access_token>


Body:

{
  "name": "Alice",
  "email": "alice@example.com",
  "phone": "+380501234567"
}

2. Отримати всі контакти

GET /contacts/?skip=0&limit=10
Headers:

Authorization: Bearer <access_token>

3. Отримати один контакт

GET /contacts/1
Headers:

Authorization: Bearer <access_token>

4. Оновити контакт (PUT)

PUT /contacts/1

{
  "name": "Alice Updated",
  "email": "alice@newmail.com",
  "phone": "+380971112233"
}

5. Часткове оновлення (PATCH)

PATCH /contacts/1

{
  "phone": "+380671234567"
}

6. Видалити контакт

DELETE /contacts/1

🧪 Приклади cURL
Логін
curl -X POST http://127.0.0.1:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"secret123"}'

Додавання контакту
curl -X POST http://127.0.0.1:8000/contacts/ \
  -H "Authorization: Bearer ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@example.com","phone":"+380501234567"}'


✨ Автор

👩‍💻 Natala Bodnarcuk