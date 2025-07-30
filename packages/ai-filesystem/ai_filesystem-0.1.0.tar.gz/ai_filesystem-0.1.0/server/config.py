from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str
    supabase_url: str
    supabase_anon_key: str
    max_file_size: int = 10485760
    rate_limit_per_minute: int = 100
    dev_mode: bool = False  # Skip auth when True
    
    class Config:
        env_file = ".env"


settings = Settings()