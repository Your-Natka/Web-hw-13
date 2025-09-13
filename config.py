from pydantic import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    DATABASE_URL: str
    REDIS_URL: str
    SMTP_HOST: str
    SMTP_PORT: int
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    RATE_LIMIT_PER_MINUTE: int = 10

    class Config:
        env_file = ".env"

settings = Settings()
