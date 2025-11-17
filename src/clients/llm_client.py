from typing import Self
from openai import OpenAI
from loguru import logger

from src.models.config import AppConfig
from src.interfaces.client import IBaseClient


class LLMClient(IBaseClient):
    _instance = None

    def __init__(self, client: OpenAI, model_name: str) -> None:
        self.model_name = model_name
        self.client = client

    @classmethod
    def create(cls, config: AppConfig) -> Self:
        if cls._instance is None:
            cls._instance = cls._create_client(config=config)
        return cls._instance

    @classmethod
    def _create_client(cls, config: AppConfig) -> Self:
        client = OpenAI(api_key=config.LLM_API_KEY, base_url=config.LLM_BASE_URL)
        model_name = config.LLM_MODEL_NAME

        logger.success("LLM-client succes initialized")

        return cls(client=client, model_name=model_name)
