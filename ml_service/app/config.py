from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "ml-rating-service"
    model_version: str = "v1.0"
    model_name: str = "all-MiniLM-L6-v2"

    huggingface_model_id: str = ""
    huggingface_token: str = ""
    use_huggingface: bool = False
    models_cache_dir: str = "./models_cache"

    device: str = "cuda:0"
    max_scenes: int = 1000

    log_level: str = "INFO"
    json_logs: bool = False
    enable_metrics: bool = True

    class Config:
        env_file = ".env"
        env_prefix = "ML_"


settings = Settings()
