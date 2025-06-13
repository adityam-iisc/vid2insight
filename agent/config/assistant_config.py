from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict
from dotenv import load_dotenv

from agent.config import constants
from agent.config.base_config import BaseConfiguration
from agent.config.initialize_logger import logger

load_dotenv()


@dataclass(kw_only=True)
class AssistantConfiguration(BaseConfiguration):
    default_llm_model: Dict[str, str] = field(
        default_factory=lambda: ({"provider": constants.PROVIDER,
                                  "model_name": constants.MODEL_NAME}),
        metadata={
            "description": "The language model used by default in the operator"
        },
    )


if __name__ == "__main__":
    config = AssistantConfiguration()
    logger.info(config)
    logger.info(config.default_llm_model['provider'])
    logger.info(config.default_llm_model['model_name'])
    llm = config.get_model(config.default_llm_model)
    resp = llm.invoke("Hello, world!")
    logger.info(resp)
