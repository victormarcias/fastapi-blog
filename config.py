from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    database_url: str = ""
    
    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    max_upload_size_bytes: int = 3 * 1024 * 1024
    posts_per_page: int = 10
    posts_per_user: int = 3
    reset_token_expire_minutes: int = 60
    
    # Email Configuration Settings
    mail_server: str = "localhost"
    mail_port: int = 587
    mail_username: str = ""
    mail_password: SecretStr = SecretStr("")
    mail_from: str = "noreply@example.com"
    mail_use_tls: bool = True
    
    frontend_url: str = "http://localhost:8000"
    
    # S3 Configuration
    s3_bucket_name: str
    s3_region: str = "us-east-2"
    s3_access_key_id: SecretStr | None = None
    s3_secret_access_key: SecretStr | None = None
    s3_endpoint_url: str | None = None
#
#
### SETTINGS __INIT__
settings = Settings()