from enum import StrEnum


class StatusEnum(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"


class NotificationTypeEnum(StrEnum):
    EMAIL = "email"
    SMS = "sms"