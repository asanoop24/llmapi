from tortoise import Tortoise, fields, run_async
from tortoise.models import Model

from llmapi.utils.database import DB_URI


class User(Model):  # type: ignore
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=100)
    email = fields.CharField(max_length=100, index=True, unique=True)
    api_key = fields.CharField(max_length=100)
    created_at = fields.DatetimeField(auto_now_add=True)


async def db_init(db_url=None):
    await Tortoise.init(db_url=DB_URI, modules={"models": ["llmapi.models.db.user"]})
    await Tortoise.generate_schemas()


if __name__ == "__main__":
    run_async(db_init())
