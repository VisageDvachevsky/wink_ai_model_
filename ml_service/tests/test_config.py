from ml_service.app.config import Settings


def test_settings_default_values():
    settings = Settings()
    assert settings.service_name == "ml-rating-service"
    assert settings.model_version == "v1.0"
    assert settings.model_name == "all-MiniLM-L6-v2"
    assert settings.device == "cuda:0"
    assert settings.max_scenes == 1000


def test_settings_environment_override(monkeypatch):
    monkeypatch.setenv("ML_MODEL_VERSION", "v2.5")
    monkeypatch.setenv("ML_DEVICE", "cpu")
    monkeypatch.setenv("ML_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("ML_ENABLE_METRICS", "false")

    settings = Settings()
    assert settings.model_version == "v2.5"
    assert settings.device == "cpu"
    assert settings.log_level == "DEBUG"
    assert settings.enable_metrics is False


def test_settings_huggingface_config(monkeypatch):
    monkeypatch.setenv("ML_USE_HUGGINGFACE", "true")
    monkeypatch.setenv("ML_HUGGINGFACE_MODEL_ID", "bert-base-uncased")
    monkeypatch.setenv("ML_HUGGINGFACE_TOKEN", "hf_test_token")

    settings = Settings()
    assert settings.use_huggingface is True
    assert settings.huggingface_model_id == "bert-base-uncased"
    assert settings.huggingface_token == "hf_test_token"
