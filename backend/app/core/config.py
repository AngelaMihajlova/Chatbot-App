from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Superadmin (seeded on first boot)
    SUPERADMIN_EMAIL: str = "superadmin@example.com"
    SUPERADMIN_PASSWORD: str = "changeme"
    SUPERADMIN_USERNAME: str = "superadmin"

    # PostgreSQL
    DATABASE_URL: str = "postgresql://chatbot:chatbot@localhost:5432/chatbot"

    # OpenAI
    OPENAI_API_KEY: str = ""
    EMBED_MODEL: str = "text-embedding-3-small"
    CHAT_MODEL: str = "gpt-4o-mini"

    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "documents"

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # MinIO (local S3-compatible)
    MINIO_ENDPOINT: str = "http://localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "documents"

    # AWS (used when storage/dynamo mode is switched to aws)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = ""
    AWS_DYNAMO_REGION: str = "us-east-1"

    # DynamoDB Local
    DYNAMO_LOCAL_ENDPOINT: str = "http://localhost:8000"
    DYNAMO_SESSIONS_TABLE: str = "ChatSessions"
    DYNAMO_MESSAGES_TABLE: str = "Messages"

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"


settings = Settings()
