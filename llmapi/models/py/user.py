import uuid

from pydantic import BaseModel
from tortoise import Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator

from llmapi.models.db.user import User as UserTable

User = pydantic_model_creator(UserTable)


class UserId(BaseModel):
    id: uuid.UUID


class UserEmail(BaseModel):
    email: str


class UserAPIKey(UserId):
    api_key: str


class UserRegister(UserEmail):
    name: str = "Anoop"
    password: str
    is_admin: bool = False


class UserLogin(UserEmail):
    password: str


class UserToken(UserEmail):
    username: str
    access_token: str
    token_type: str = "bearer"
