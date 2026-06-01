from pydantic import BaseModel
from models.enums import NotificationTypeEnum, StatusEnum


class CreateRequestBody(BaseModel):
    user_input: str


class CreateRequestResponse(BaseModel):
    id: str


class StatusResponse(BaseModel):
    id: str
    status: StatusEnum


class NotificationPayload(BaseModel):
    to: str
    message: str
    type: NotificationTypeEnum