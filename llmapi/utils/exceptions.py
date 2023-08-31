from fastapi import HTTPException, status
from openai.error import AuthenticationError


class UserAlreadyExists(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="username already exists")


class OpenAIAuthenticationError(AuthenticationError):
    def __init__(self):
        super().__init__()


class InvalidAPIKey(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid api key")


class InvalidJWTSecret(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid jwt secret")


class InvalidPassword(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid password")


class InvalidToken(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token", headers={"WWW-Authenticate": "Bearer"})
