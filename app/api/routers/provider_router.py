from fastapi import APIRouter, HTTPException

from models.schemas import CreateRequestBody, CreateRequestResponse, StatusResponse
from services import notification_service

router = APIRouter(prefix="/v1/requests", tags=["requests"])


@router.post("", response_model=CreateRequestResponse, status_code=201)
async def create_request(body: CreateRequestBody):
    request_id: str = await notification_service.create_request(body.user_input)
    return CreateRequestResponse(id=request_id)


@router.post("/{request_id}/process", status_code=202)
async def process_request(request_id: str):
    entry: dict | None = await notification_service.process_request(request_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"id": entry["id"], "status": entry["status"]}


@router.get("/{request_id}", response_model=StatusResponse)
async def get_request(request_id: str):
    entry: dict | None = await notification_service.get_request(request_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return StatusResponse(id=request_id, status=entry["status"])
