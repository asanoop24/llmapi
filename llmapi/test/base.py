from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMConfig:
    model_id: str
    # prompt_cost_1k_tokens_usd: float = None
    # completion_cost_1k_tokens_usd: float = None


class LLM(ABC):
    def __init__(self, config: LLMConfig = None):
        self.config = config
        self.model_id = config.model_id

    @abstractmethod
    def generate_completion(self, prompt: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def log_costs(self, completion_response: dict) -> None:
        raise NotImplementedError
