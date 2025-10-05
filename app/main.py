from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.responses import JSONResponse
from app.rate_limit import limiter
from app.database import Base, engine
from app import models  # ensure models imported for metadata
from app.routes import auth, contacts

# create tables if not exist (quick dev way)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Contacts API with Auth & Verification")

# CORS
origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Rate limit
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Too Many Requests"})

# include routers
app.include_router(auth.router)
app.include_router(contacts.router)
