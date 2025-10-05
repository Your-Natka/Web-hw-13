import requests
import time

BASE_URL = "http://localhost:8080"
EMAIL = f"testuser{int(time.time())}@example.com"
PASSWORD = "password123"

# 1️⃣ Реєстрація користувача
print("1️⃣ Register user...")
resp = requests.post(f"{BASE_URL}/auth/register", json={"email": EMAIL, "password": PASSWORD})
print("Status:", resp.status_code, "Response:", resp.json())
if resp.status_code != 200:
    print("User may already exist, skipping registration.")

# 2️⃣ Перевірка листа у MailHog
print("\n2️⃣ Checking MailHog for verification email...")
mailhog_resp = requests.get("http://localhost:8025/api/v2/messages")
messages = mailhog_resp.json().get("items", [])
verification_link = None
for msg in messages:
    if EMAIL in msg["Content"]["Headers"].get("To", []):
        body = msg["Content"]["Body"]
        # шукаємо /auth/verify?token=...
        start = body.find("/auth/verify?token=")
        if start != -1:
            end = body.find("\n", start)
            verification_link = BASE_URL + body[start:end].strip()
            break

if verification_link:
    print("Found verification link:", verification_link)
    verify_resp = requests.get(verification_link)
    print("Verification status:", verify_resp.status_code, "Response:", verify_resp.json())
else:
    print("No verification email found. Skipping verification.")

# 3️⃣ Логін
print("\n3️⃣ Login...")
login_resp = requests.post(f"{BASE_URL}/auth/token", data={"username": EMAIL, "password": PASSWORD})
print("Status:", login_resp.status_code)
token = None
if login_resp.status_code == 200:
    token = login_resp.json().get("access_token")
    print("Token:", token)
else:
    print("Login failed:", login_resp.json())

headers = {"Authorization": f"Bearer {token}"} if token else {}

# 4️⃣ Перевірка Redis (опціонально)
print("\n4️⃣ Checking Redis cache...")
import redis
r = redis.Redis(host="localhost", port=6379, db=0)
print("Redis keys:", r.keys())

# 5️⃣ Завантаження аватара
import os
avatar_path = "test_avatar.png"
if os.path.exists(avatar_path) and token:
    print("\n5️⃣ Uploading avatar...")
    with open(avatar_path, "rb") as f:
        files = {"file": f}
        avatar_resp = requests.put(f"{BASE_URL}/contacts/avatar", files=files, headers=headers)
        print("Status:", avatar_resp.status_code, "Response:", avatar_resp.json())
else:
    print("\n5️⃣ Avatar file not found or no token, skipping upload.")
