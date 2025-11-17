import os

from pydantic import BaseModel, Field
from src.common.const import DEFAULT_PRIVATE_JWT_KEY, DEFAULT_PUBLIC_JWT_KEY


class DBConfig(BaseModel):
    DB_URL: str = Field(default="postgres://postgres:postgres@localhost:5432/postgres")


class JWTConfig(BaseModel):
    JWT_PUBLIC_KEY: str = Field(default=DEFAULT_PUBLIC_JWT_KEY)
    JWT_PRIVATE_KEY: str = Field(default=DEFAULT_PRIVATE_JWT_KEY)


class LLMConfig(BaseModel):
    LLM_BASE_URL: str = Field(...)
    LLM_MODEL_NAME: str = Field(...)
    LLM_API_KEY: str = Field(default="")


class AppConfig(BaseModel):
    db_config: DBConfig
    jwt_config: JWTConfig
    llm_config: LLMConfig

    @classmethod
    def create(cls):
        envs = os.environ

        db_config = DBConfig(**envs)
        jwt_config = JWTConfig(**envs)
        llm_config = LLMConfig(**envs)

        return AppConfig(
            db_config=db_config, jwt_config=jwt_config, llm_config=llm_config
        )
