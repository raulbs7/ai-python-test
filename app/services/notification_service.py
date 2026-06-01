import asyncio
import uuid

import clients.provider_client as provider_client
from models.enums import StatusEnum
from services.parser_service import parse_response
from store import requests_store


async def create_request(user_input: str) -> str:
    request_id: str = str(uuid.uuid4())
    requests_store[request_id] = {
        "id": request_id,
        "user_input": user_input,
        "status": StatusEnum.QUEUED,
    }
    return request_id


async def _extract_and_notify(request_id: str) -> None:
    entry: dict = requests_store[request_id]
    try:
        content: str = await provider_client.extract_notification(entry["user_input"])
        notification: dict | None = parse_response(content)
        if notification is None:
            entry["status"] = StatusEnum.FAILED
            return
        await provider_client.send_notification(
            to=notification["to"],
            message=notification["message"],
            type=notification["type"],
        )
        entry["status"] = StatusEnum.SENT
    except Exception:
        entry["status"] = StatusEnum.FAILED


async def process_request(request_id: str) -> dict | None:
    entry: dict | None = requests_store.get(request_id)
    if entry is None:
        return None
    entry["status"] = StatusEnum.PROCESSING
    asyncio.create_task(_extract_and_notify(request_id))
    return entry


async def get_request(request_id: str) -> dict | None:
    return requests_store.get(request_id)
