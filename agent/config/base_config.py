from __future__ import annotations
from dataclasses import dataclass,  fields
from typing import Optional, Type, TypeVar
from langchain_core.runnables import RunnableConfig, ensure_config
from langchain_core.language_models import BaseChatModel
from langchain.chat_models import init_chat_model
from agent.config.initialize_logger import logger
from dotenv import load_dotenv
import os
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
    def get_model(cls: Type[T],model: dict) -> BaseChatModel:
        """Load a chat model from the specified dict.
        Args:
            dict(str,str): Dictionary with name and provider for the model'.
        """
        provider = model['provider']
        model_name = model['model_name']
        logger.info(f"Loading model {model['model_name']} from provider {provider}")
        match provider:
            case "openai":
                model_kwargs = {}
                return init_chat_model(model_name, model_provider=provider, **model_kwargs)                
            case "azure_openai":
                model_kwargs = {"api_version":os.environ["AZURE_OPENAI_API_VERSION"]}
                return init_chat_model(model_name, model_provider=provider, **model_kwargs)
            case "google_genai":
                return init_chat_model(model_name, model_provider=provider)
            case _:
                raise ValueError(f"Unsupported: {provider}")


T = TypeVar("T", bound=BaseConfiguration)
