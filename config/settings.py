from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Azure OpenAI
    azure_openai_endpoint: str
    azure_openai_key: str
    azure_openai_deployment: str
    azure_openai_api_version: str = "2024-12-01-preview"
    azure_openai_model: str = "gpt-5-mini"
    
    # Tavily
    tavily_api_key: str
    
    # Database
    database_path: str = "./data/vector_store.db"
    
    # Logging
    log_level: str = "INFO"
    
    # Agent Configuration
    max_iterations: int = 10
    max_context_tokens: int = 8000
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5
    
    # Temperature (fixed for Azure)
    temperature: float = 1.0


settings = Settings()