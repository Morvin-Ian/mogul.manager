from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    database_url: str

    secret_key: SecretStr
    refresh_secret_key: SecretStr | None = None
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30
    # None = infer from frontend_url scheme (https → True); set explicitly in prod
    cookie_secure: bool | None = None
    max_upload_size_bytes: int = 5 * 1024 * 1024
    posts_per_page: int = 10
    reset_token_expire_minutes: int = 60

    s3_account_id: SecretStr
    s3_access_key_id: SecretStr
    s3_secret_access_key: SecretStr
    s3_bucket_name: str
    s3_custom_domain: str
    s3_endpoint_url: str = ""

    mail_server: str = "localhost"
    mail_port: int = 587
    mail_username: str = ""
    mail_password: SecretStr = SecretStr("")
    mail_from: str = "noreply@example.com"
    mail_use_tls: bool = True

    frontend_url: str = "http://localhost:3000"

    deepseek_api_key: SecretStr = SecretStr("")
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: SecretStr = SecretStr("")
    google_redirect_url: str = ""


settings = Settings()  # type: ignore[call-arg]
