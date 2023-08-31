from enum import Enum


class RequestTaskEnum(str, Enum):
    CHAT_COMPLETION = "chat_completion"
    TEXT_COMPLETION = "text_completion"


class ResponseStatusEnum(str, Enum):
    SUCCESS = 200
    AUTHENTICATION_ERROR = 401
    RATE_LIMIT_ERROR = 429
