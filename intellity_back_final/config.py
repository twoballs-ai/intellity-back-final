from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    REFRESH_TOKEN_EXPIRE_DAYS: int
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    SQLALCHEMY_DATABASE_URL: str

    # Email settings
    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_TLS: bool
    MAIL_SSL: bool

    class Config:
        env_file = ".env"


settings = Settings()
