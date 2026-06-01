import asyncio

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from config import settings

SYSTEM_PROMPT = (
    "You are a notification extraction assistant. "
    "Extract the recipient, message, and channel from the user's request. "
    "Respond ONLY with a JSON object in this exact format, no extra text:\n"
    '{"to": "<email or phone number>", "message": "<text to send>", "type": "<email or sms>"}\n'
    "Rules:\n"
    '- "type" must be exactly "email" or "sms"\n'
    '- "to" must be the raw email address or phone number\n'
    '- "message" must be the content to deliver'
)

semaphore = asyncio.Semaphore(settings.provider_max_concurrent)
client = httpx.AsyncClient(timeout=30.0)


def is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in (429, 500)
    return isinstance(exc, httpx.RequestError)


@retry(
    stop=stop_after_attempt(settings.provider_max_retries),
    wait=wait_exponential(
        multiplier=settings.provider_retry_multiplier,
        min=settings.provider_retry_min_wait,
        max=settings.provider_retry_max_wait,
    ),
    retry=retry_if_exception(is_retryable),
    reraise=True,
)
async def extract_notification(user_input: str) -> str:
    async with semaphore:
        response = await client.post(
            f"{settings.provider_base_url}/v1/ai/extract",
            headers={"X-API-Key": settings.provider_api_key},
            json={
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_input},
                ]
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


@retry(
    stop=stop_after_attempt(settings.provider_max_retries),
    wait=wait_exponential(
        multiplier=settings.provider_retry_multiplier,
        min=settings.provider_retry_min_wait,
        max=settings.provider_retry_max_wait,
    ),
    retry=retry_if_exception(is_retryable),
    reraise=True,
)
async def send_notification(to: str, message: str, type: str) -> None:
    async with semaphore:
        response = await client.post(
            f"{settings.provider_base_url}/v1/notify",
            headers={"X-API-Key": settings.provider_api_key},
            json={"to": to, "message": message, "type": type},
        )
        response.raise_for_status()
