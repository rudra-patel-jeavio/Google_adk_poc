import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # API Keys
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    
    # Google Cloud
    google_cloud_project: Optional[str] = Field(None, env="GOOGLE_CLOUD_PROJECT")
    google_application_credentials: Optional[str] = Field(None, env="GOOGLE_APPLICATION_CREDENTIALS")
    
    # Application Settings
    streamlit_port: int = Field(8501, env="STREAMLIT_PORT")
    debug_mode: bool = Field(True, env="DEBUG_MODE")
    default_model: str = Field("gpt-4", env="DEFAULT_MODEL")
    max_tokens: int = Field(2000, env="MAX_TOKENS")
    temperature: float = Field(0.7, env="TEMPERATURE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_model_config() -> Dict[str, Any]:
    """Get model configuration for litellm."""
    return {
        "openai": {
            "api_key": settings.openai_api_key,
            "models": {
                "gpt_5": "gpt-5",
                "gpt_41": "gpt-4.1",
                "gpt_5_mini": "gpt-5-mini",
            }
        },
        "anthropic": {
            "api_key": settings.anthropic_api_key,
            "models": {
                "claude_4_sonnet": "claude-sonnet-4-20250514",
                "claude_37_sonnet": "claude-3-7-sonnet-20250219",
            }
        },
        "google": {
            "api_key": settings.google_api_key,
            "models": {
                "gemini_25_pro": "gemini-2.5-pro",
                "gemini_25_flash": "gemini-2.5-flash",
            }
        }
    } 