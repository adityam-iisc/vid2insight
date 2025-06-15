from __future__ import annotations

import os
from dataclasses import dataclass, fields
from typing import Optional, Type, TypeVar

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableConfig, ensure_config

from agent.config.initialize_logger import logger

load_dotenv()


@dataclass(kw_only=True)
class BaseConfiguration:

    @classmethod
    def from_runnable_config(
            cls: Type[T], config: Optional[RunnableConfig] = None
    ) -> T:
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable.items() if k in _fields})

    @classmethod
    def get_model(cls: Type[T], model: dict) -> BaseChatModel:
        """Load a chat model from the specified dict.
        Args:
            dict(str,str): Dictionary with name and provider for the model'.
        """
        provider = model['provider']
        model_name = model['model_name']
        logger.info(f"Loading model {model['model_name']} from provider {provider}")

        model_instance = None
        match provider:
            case "openai":
                model_kwargs = {}
                model_instance = init_chat_model(model_name, model_provider=provider, **model_kwargs)
            case "azure_openai":
                model_kwargs = {"api_version": os.environ["AZURE_OPENAI_API_VERSION"]}
                model_instance = init_chat_model(model_name, model_provider=provider, **model_kwargs)
            case "google_genai":
                model_instance = init_chat_model(model_name, model_provider=provider)
            case _:
                raise ValueError(f"Unsupported: {provider}")

        logger.info(f"Successfully loaded model: {model_name} from provider: {provider}")
        return model_instance


T = TypeVar("T", bound=BaseConfiguration)
