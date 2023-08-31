from openai.error import AuthenticationError
from tortoise import exceptions as TortoiseExceptions

from llmapi.models.db.user import User as UserTable
from llmapi.models.py.user import User
from llmapi.utils import exceptions as AuthExceptions


async def validate_user_exists(api_key: str) -> User:
    """checks if the user exists in the database

    Args:
        api_key (str): api key assigned to the user

    Raises:
        AuthExceptions.Invalid APIKey: APIKey does not exist in the database

    Returns:
        User: user details
    """

    try:
        user = await UserTable.get(api_key=api_key)
        return user
    except TortoiseExceptions.DoesNotExist:
        raise AuthExceptions.InvalidAPIKey()


async def validate_user_exists(**attributes) -> User:
    """checks if the user exists in the database

    Args:
        api_key (str): api key assigned to the user

    Raises:
        AuthExceptions.Invalid APIKey: APIKey does not exist in the database

    Returns:
        User: user details
    """

    try:
        user = await UserTable.get(**attributes)
        return user
    except TortoiseExceptions.DoesNotExist:
        raise AuthenticationError()
