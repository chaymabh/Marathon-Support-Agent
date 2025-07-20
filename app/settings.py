from pydantic import  Field
from pydantic_settings  import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    
    api_key: str = Field(..., env="API_KEY")
    openai_server: str = Field('openai', env="OPENAI_SERVER")
    openai_model: str = Field('gpt-4o', env="OPENAI_MODEL")
    openai_model_endpoint: Optional[str] = Field(None, env="OPENAI_MODEL_ENDPOINT")

    log_file: str = Field('app.log', env="LOG_FILE")
    call_responce_log_file: str = Field('call_responce.log', env="CALL_responce_LOG_FILE")

    verbose: bool = Field(False, env="VERBOSE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'allow'

settings = Settings()
