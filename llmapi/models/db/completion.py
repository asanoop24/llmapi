from tortoise import Tortoise, fields, run_async
from tortoise.models import Model

from llmapi.models.enums import RequestTaskEnum
from llmapi.utils.database import DB_URI


class OpenAIRequest(Model):  # type: ignore
    id = fields.UUIDField(pk=True)
    task = fields.CharEnumField(enum_type=RequestTaskEnum, default=RequestTaskEnum.CHAT_COMPLETION)
    user = fields.ForeignKeyField(model_name="models.User", to_field="id", null=True)
    status = fields.IntField(null=True)
    prompt = fields.TextField(default="", null=True)
    response = fields.JSONField(default=[], null=True)
    prompt_tokens = fields.IntField(null=True)
    completion_tokens = fields.IntField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)


async def db_init(db_url=None):
    await Tortoise.init(db_url=DB_URI, modules={"models": ["llmapi.models.db.completion"]})
    await Tortoise.generate_schemas()


if __name__ == "__main__":
    run_async(db_init())
