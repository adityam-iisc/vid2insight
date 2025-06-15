from __future__ import annotations
from dotenv import load_dotenv
import os

from dataclasses import dataclass, field
from typing import Dict

from langchain.chat_models import init_chat_model
from langchain_google_genai import ChatGoogleGenerativeAI

from agent.config.base_config import BaseConfiguration
from agent.config import constants
from agent.config.initialize_logger import logger

load_dotenv('/Users/admukhop/Desktop/iisc/Deep Learning/project/vid2insight/agent/')


@dataclass(kw_only=True)
class AssistantConfiguration(BaseConfiguration):
    default_llm_model: Dict[str, str] = field(
        default_factory=lambda: ({"provider": constants.PROVIDER,
                                  "model_name": constants.MODEL_NAME}),
        metadata={
            "description": "The language model used by default in the operator"
        },
    )

    def get_model(self, model_config: Dict[str, str]):
        api_key = os.getenv('GEMINI_API_KEY', '')
        return ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    temperature=0.6,
                    max_retries=2,
                    google_api_key=api_key,
                )


# if __name__ == "__main__":
#     config = AssistantConfiguration()
#     logger.info(config)
#     logger.info(config.default_llm_model['provider'])
#     logger.info(config.default_llm_model['model_name'])
#     llm = config.get_model(config.default_llm_model)
#     resp = llm.invoke("Hello, world!")
#     logger.info(resp)