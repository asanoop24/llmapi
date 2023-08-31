import uuid

from fastapi import APIRouter, Depends, Form, Query
from fastapi.security import OAuth2PasswordRequestForm

from llmapi.models.db.user import User as UserTable
from llmapi.models.py.user import User, UserAPIKey, UserId, UserToken
from llmapi.utils import authentication as Auth
from llmapi.utils import exceptions as E
from llmapi.utils import validations as V

router = APIRouter(prefix="", tags=["auth"])


@router.post("/register", response_model=UserId)
async def create_user(
    name: str = Form(default="", description="Name of the user"),
    email: str = Form(default=..., description="Email of the user"),
    secret: str = Form(..., description="Secret"),
):
    try:
        user = await UserTable.get(email=email).values()
    except:
        user = None

    if user:
        raise E.UserAlreadyExists()

    if not Auth.verify_jwt_secret(secret):
        raise E.InvalidJWTSecret()

    api_key = Auth.generate_api_key()

    user_id = uuid.uuid4()
    await UserTable.create(
        id=user_id,
        name=name,
        email=email,
        api_key=api_key,
    )

    return UserId(id=user_id)


@router.get("/{user_id}/apikey")
async def fetch_api_key(user_id: str):
    user: UserTable = await V.validate_user_exists(id=user_id)
    api_key = user.api_key
    return UserAPIKey(id=user_id, api_key=api_key)


@router.post("/login", response_model=UserToken)
async def login_with_ket(data: OAuth2PasswordRequestForm = Depends()):
    email, password = data.username, data.password

    try:
        user = await UserTable.get(email=email).values()
    except:
        user = None

    if not user:
        raise E.InvalidUsername()

    is_authenticated = Auth.authenticate_with_password(user["password"], password)
    if not is_authenticated:
        raise E.InvalidPassword()

    access_token = Auth.generate_access_token(data={"sub": email})

    return UserToken(username=email, email=email, access_token=access_token)
