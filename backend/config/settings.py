"""
Application Settings and Configuration
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_title: str = "Google ADK Multi-Agent API"
    api_version: str = "1.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Google ADK Configuration
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    gemini_model: str = "gemini-2.0-flash"
    
    # OpenAI Configuration (for LiteLLM)
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    
    # Anthropic Configuration (for LiteLLM)
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # Database Configuration
    database_url: str = "sqlite:///./google_adk.db"
    
    # Redis Configuration (for caching and sessions)
    redis_url: str = "redis://localhost:6379"
    redis_enabled: bool = False
    
    # Authentication
    jwt_secret_key: str = Field(default="your-secret-key-change-in-production", env="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Streaming Configuration
    streaming_update_interval_ms: int = 16  # 60fps
    streaming_batch_size: int = 3
    streaming_buffer_timeout_ms: int = 100
    
    # Memory Configuration
    memory_max_entries: int = 10000
    memory_cleanup_interval_hours: int = 24
    
    # Agent Configuration
    default_agent_temperature: float = 0.7
    default_agent_max_tokens: int = 2048
    default_agent_timeout_seconds: int = 30
    
    # CORS Configuration
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    
    # File Upload Configuration
    max_file_size_mb: int = 10
    allowed_file_types: List[str] = [".txt", ".pdf", ".docx", ".md", ".json", ".csv"]
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = 100
    rate_limit_enabled: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
