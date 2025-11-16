from app.core.exceptions import (
    ScriptNotFoundError,
    MLServiceError,
    MLServiceTimeoutError,
    InvalidFileError,
    FileTooLargeError,
)


def test_script_not_found_error():
    error = ScriptNotFoundError(script_id=42)
    assert error.status_code == 404
    assert "42" in error.detail


def test_ml_service_error():
    error = MLServiceError("Connection refused")
    assert error.status_code == 503
    assert "Connection refused" in error.detail


def test_ml_service_timeout_error():
    error = MLServiceTimeoutError()
    assert error.status_code == 504
    assert "timed out" in error.detail


def test_invalid_file_error():
    error = InvalidFileError("Not a valid format")
    assert error.status_code == 400
    assert "Not a valid format" in error.detail


def test_file_too_large_error():
    error = FileTooLargeError(max_size_mb=10)
    assert error.status_code == 413
    assert "10MB" in error.detail
