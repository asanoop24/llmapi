from typing import Optional

from pydantic import BaseModel


class OpenAIErrorResponse(BaseModel):
    message: str
    type: str
    param: Optional[str] = None
    code: Optional[str] = None
