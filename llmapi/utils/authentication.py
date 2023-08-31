import secrets
from datetime import datetime, timedelta
from os import getenv as env

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

# to get a string like this run:
# openssl rand -hex 32
JWT_SECRET = env("JWT_SECRET")
ALGORITHM = env("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(env("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
APIKEY_LENGTH = 32

crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=True)


def generate_hash(s: str):
    return crypt.hash(s)


def authenticate_with_password(hash: str, plain: str):
    is_authenticated = crypt.verify(plain, hash)
    return is_authenticated


def generate_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_with_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except:
        return None


def generate_api_key():
    api_key = secrets.token_urlsafe(APIKEY_LENGTH)
    return api_key


def verify_api_key(hash: str, api_key: str):
    is_valid = crypt.verify(api_key, hash)
    return is_valid


def verify_jwt_secret(secret: str) -> bool:
    return secret == JWT_SECRET
