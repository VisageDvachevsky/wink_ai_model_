import asyncio
import httpx
from loguru import logger
from ..core.config import settings
from ..core.exceptions import MLServiceError, MLServiceTimeoutError


class MLServiceClient:
    def __init__(self):
        self.base_url = settings.ml_service_url
        self.timeout = settings.ml_service_timeout
        self.max_retries = settings.ml_service_max_retries
        self.retry_delay = settings.ml_service_retry_delay

    async def rate_script(self, text: str, script_id: str | None = None) -> dict:
        last_error = None

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/rate_script",
                        json={"text": text, "script_id": script_id},
                    )
                    response.raise_for_status()
                    return response.json()

            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(
                    f"ML service timeout on attempt {attempt + 1}/{self.max_retries}"
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2**attempt))
                    continue
                raise MLServiceTimeoutError()

            except httpx.HTTPStatusError as e:
                logger.error(f"ML service HTTP error: {e.response.status_code}")
                raise MLServiceError(f"HTTP {e.response.status_code}")

            except httpx.RequestError as e:
                last_error = e
                logger.warning(
                    f"ML service connection error on attempt {attempt + 1}/{self.max_retries}: {e}"
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2**attempt))
                    continue
                raise MLServiceError(f"Connection failed: {str(e)}")

        if last_error:
            raise MLServiceError(f"Max retries exceeded: {str(last_error)}")

    async def health_check(self) -> dict:
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"ML service health check failed: {e}")
                raise MLServiceError(f"Health check failed: {str(e)}")


ml_client = MLServiceClient()
