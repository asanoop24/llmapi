import uuid
from http import HTTPStatus
from os import getenv as env

import openai
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from openai.error import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    InvalidRequestError,
    RateLimitError,
    ServiceUnavailableError,
    Timeout,
)

from llmapi.models.db.completion import OpenAIRequest as OpenAIRequestDB
from llmapi.models.db.user import User as UserDB
from llmapi.models.enums import RequestTaskEnum, ResponseStatusEnum
from llmapi.models.py.completion import OpenAIErrorResponse
from llmapi.utils.validations import validate_user_exists

router = APIRouter(prefix="/v1", tags=["completion"])


def mask_api_key(unmasked: str) -> str:
    return unmasked[:6] + "*" * (len(unmasked) - 10) + unmasked[-4:]


def create_error_response(status_code: HTTPStatus, message: str, error_code: str) -> JSONResponse:
    return JSONResponse(
        dict(
            error=OpenAIErrorResponse(message=message, type="invalid_request_error", code=error_code).model_dump(),
        ),
        status_code=status_code,
    )


@router.post("/chat/completions")
async def generate_chat_completion(request: Request):
    params = await request.json()
    auth_header = request.headers.get("authorization")
    api_key = auth_header.split()[1]
    messages = params.pop("messages")
    model = params.pop("model")

    user, completion_response, error_response = None, None, None

    try:
        user: UserDB = await validate_user_exists(api_key=api_key)
    except AuthenticationError as err:
        error_response = create_error_response(
            status_code=HTTPStatus.UNAUTHORIZED.value,
            message=f"Incorrect API key provided: {mask_api_key(api_key)}. You can ask for a new API key from your admin in case you forgot the API key.",
            error_code="invalid_api_key",
        )

    if error_response is None:
        try:
            completion_response = await openai.ChatCompletion.acreate(
                model=model, messages=messages, api_key=env("OPENAI_API_KEY"), **params
            )
        except (
            APIError,
            Timeout,
            RateLimitError,
            APIConnectionError,
            InvalidRequestError,
            AuthenticationError,
            ServiceUnavailableError,
        ) as err:
            error_response = create_error_response(
                status_code=err.http_status,
                message=err.json_body["error"]["message"],
                error_code=err.json_body["error"]["code"],
            )

    response = completion_response if completion_response is not None else error_response
    status_code = ResponseStatusEnum.SUCCESS if completion_response is not None else error_response.status_code
    prompt_tokens = completion_response.usage.prompt_tokens if completion_response is not None else None
    completion_tokens = completion_response.usage.completion_tokens if completion_response is not None else None

    await OpenAIRequestDB.create(
        id=uuid.uuid4(),
        task=RequestTaskEnum.CHAT_COMPLETION,
        user=user,
        status=status_code,
        prompt=messages,
        response=response.body if hasattr(response, "body") else response,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
    )

    return response


@router.post("/completions")
async def generate_completion(request: Request):
    params = await request.json()
    auth_header = request.headers.get("authorization")
    api_key = auth_header.split()[1]
    prompt = params.pop("prompt")
    model = params.pop("model")

    user, completion_response, error_response = None, None, None

    try:
        user: UserDB = await validate_user_exists(api_key=api_key)
    except AuthenticationError as err:
        error_response = create_error_response(
            status_code=HTTPStatus.UNAUTHORIZED.value,
            message=f"Incorrect API key provided: {mask_api_key(api_key)}. You can ask for a new API key from your admin in case you forgot the API key.",
            error_code="invalid_api_key",
        )

    if error_response is None:
        try:
            completion_response = await openai.Completion.acreate(model=model, prompt=prompt, api_key=env("OPENAI_API_KEY"), **params)
        except (
            APIError,
            Timeout,
            RateLimitError,
            APIConnectionError,
            InvalidRequestError,
            AuthenticationError,
            ServiceUnavailableError,
        ) as err:
            error_response = create_error_response(
                status_code=err.http_status,
                message=err.json_body["error"]["message"],
                error_code=err.json_body["error"]["code"],
            )

    response = completion_response if completion_response is not None else error_response
    status_code = ResponseStatusEnum.SUCCESS if completion_response is not None else error_response.status_code
    prompt_tokens = completion_response.usage.prompt_tokens if completion_response is not None else None
    completion_tokens = completion_response.usage.completion_tokens if completion_response is not None else None

    await OpenAIRequestDB.create(
        id=uuid.uuid4(),
        task=RequestTaskEnum.TEXT_COMPLETION,
        user=user,
        status=status_code,
        prompt=prompt,
        response=response if completion_response is not None else response.body,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
    )

    return response
