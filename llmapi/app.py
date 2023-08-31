from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

from llmapi.routers import completion, user
from llmapi.utils.database import DB_URI
from llmapi.utils.logging import init_logger

load_dotenv()
init_logger()
app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(completion.router)

register_tortoise(
    app,
    db_url=DB_URI,
    modules={
        "models": [
            "llmapi.models.db.user",
            "llmapi.models.db.completion",
        ]
    },
    generate_schemas=True,
    add_exception_handlers=False,
)


@app.on_event("startup")
async def startup_event():
    pass


@app.on_event("shutdown")
async def shutdown():
    await Tortoise.close_connections()


@app.get("/health")
async def check_api_health():
    return {"message": "ok"}


@app.get("/health1")
async def check_api_health():
    # return RedirectResponse(url="http://localhost:8000/mlflow", status_code=302)
    return {"message": "not ok"}


# @app.get("/hello")
# async def secure_hello(is_authenticated: bool = Depends(authenticate_with_token)):
#     if not is_authenticated:
#         raise E.INVALID_TOKEN

#     # db_user: db_models.User = crud.get_user_by_username(db, username)
#     # user = py_models.User(username=db_user.username, id=db_user.id)

#     return {"message": "you are authenticated"}
