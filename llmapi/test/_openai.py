from os import getenv as env
from os import makedirs
from os.path import dirname, exists

import openai
import pandas as pd
from dotenv import load_dotenv

from llmapi.test.base import LLM, LLMConfig

load_dotenv()
from dataclasses import dataclass
from datetime import datetime

# openai.organization = env("OPENAI_ORG_ID")
openai.api_key = env("OPENAI_API_KEY")
cost_log_file = f"./costs/{datetime.now():%Y%m%d}.csv"


@dataclass
class OpenAIConfig(LLMConfig):
    openai_api_base: str
    openai_api_key: str


@dataclass
class AzureOpenAIConfig(OpenAIConfig):
    openai_api_base: str
    openai_api_type: str
    azure_openai_deployment_name: str


class OpenAILLM(LLM):
    async def generate_completion(self, prompt: str, task: str = "chat_completion") -> dict:
        # print(openai.Model.list())
        openai.api_base = self.config.openai_api_base
        openai.api_key = self.config.openai_api_key
        try:
            if task == "chat_completion":
                messages = [{"role": "user", "content": prompt}]
                completion_response = await openai.ChatCompletion.acreate(model=self.model_id, messages=messages)
                completion = completion_response.choices[0].message.content
            elif task == "completion":
                completion_response = await openai.Completion.acreate(model=self.model_id, prompt=prompt)
                completion = completion_response.choices[0].text
            return completion, completion_response
        except Exception as err:
            raise
            print(err)
            return ""

    def log_costs(self, completion_response: dict, prompt: str):
        gpt_35_turbo_4k_prompt_cost_1k_tokens_usd = 0.0015
        gpt_35_turbo_4k_completion_cost_1k_tokens_usd = 0.002
        gpt_35_turbo_16k_prompt_cost_1k_tokens_usd = 0.003
        gpt_35_turbo_16k_completion_cost_1k_tokens_usd = 0.004

        prompt_tokens = completion_response.usage.prompt_tokens
        completion_tokens = completion_response.usage.completion_tokens
        completion = completion_response.choices[0].message.content

        prompt_cost_usd = prompt_tokens * gpt_35_turbo_4k_prompt_cost_1k_tokens_usd
        completion_cost_usd = completion_tokens * gpt_35_turbo_4k_completion_cost_1k_tokens_usd

        log_item = [
            f"{datetime.now():%Y-%m-%d}",
            f"{datetime.now():%Y-%m-%d %H:%M:%S}",
            self.model,
            prompt_tokens,
            completion_tokens,
            prompt_cost_usd,
            completion_cost_usd,
            prompt_cost_usd + completion_cost_usd,
            prompt,
            completion,
        ]

        log_cols = [
            "date",
            "timestamp",
            "model",
            "prompt_tokens",
            "completion_tokens",
            "prompt_cost_usd",
            "completion_cost_usd",
            "total_cost_usd",
            "prompt",
            "completion",
        ]

        if not exists(dirname(cost_log_file)):
            makedirs(dirname(cost_log_file))

        df = pd.DataFrame(data=[log_item], columns=log_cols)
        df.to_csv(cost_log_file, mode="a", index=False, header=False)


async def test():
    config = OpenAIConfig(
        openai_api_base="http://localhost:8000/v1",
        openai_api_key=env("LLMAPI_KEY"),
        # model_id="text-davinci-003",
        model_id="gpt-3.5-turbo",
    )
    llm = OpenAILLM(config)
    # completion, compleition_response = await llm.generate_completion("what is the date on Mars today", "completion")
    completion, compleition_response = await llm.generate_completion("what is the date on Mars today", "chat_completion")
    print(completion)
    print(compleition_response)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test())
