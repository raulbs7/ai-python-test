import json
import re

from pydantic import ValidationError

from models.schemas import NotificationPayload


FIELD_ALIASES: dict[str, set[str]] = {
    "to": {"to", "To", "Recipient", "recipient", "destination", "Destination"},
    "message": {"message", "Message", "body", "Body", "text", "Text", "content", "Content"},
    "type": {"type", "Type", "channel", "Channel", "method", "Method"},
}

REFUSAL_PATTERNS: list[str] = [
    "lo siento",
    "no tengo permitido",
    "políticas de seguridad",
    "potential spam",
    "refused:",
    "flagged sensitive",
]


def _is_refusal(text: str) -> bool:
    lower: str = text.lower()
    return any(pattern in lower for pattern in REFUSAL_PATTERNS)


def _strip_markdown(text: str) -> str:
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = re.sub(r"```", "", text)
    return text.strip()


def _extract_json_substring(text: str) -> str | None:
    # Search complete JSON object first
    match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    # Fall back to truncated JSON
    match = re.search(r"\{[^{}]+", text, re.DOTALL)
    return match.group(0) if match else None


def _fix_malformed_json(text: str) -> str:
    # Close truncated JSON
    if not text.rstrip().endswith("}"):
        text = re.sub(r'[\s.]*$', '', text) + "}"
    # Single quotes to double quotes
    text = re.sub(r"'([^']*)'", r'"\1"', text)
    # Unquoted keys
    text = re.sub(r'([\{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1 "\2":', text)
    match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    return match.group(0) if match else text


def _normalize_fields(data: dict) -> dict | None:
    mapped: dict = {}
    for canonical, aliases in FIELD_ALIASES.items():
        for key in data:
            if key in aliases:
                mapped[canonical] = data[key]
                break
    try:
        return NotificationPayload.model_validate(mapped).model_dump()
    except ValidationError:
        return None


def parse_response(content: str) -> dict | None:
    if _is_refusal(content):
        return None

    text: str = _strip_markdown(content)

    json_str: str = _extract_json_substring(text)
    if json_str is None:
        return None

    try:
        data = json.loads(json_str)
        return _normalize_fields(data)
    except json.JSONDecodeError:
        pass

    fixed: str = _fix_malformed_json(json_str)
    try:
        data = json.loads(fixed)
        return _normalize_fields(data)
    except json.JSONDecodeError:
        return None
