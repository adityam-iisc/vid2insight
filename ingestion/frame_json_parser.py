import json
import re

from typing import List, Dict
from langchain_core.output_parsers import BaseOutputParser

from agent.config.initialize_logger import logger


class FrameJsonOutputParser(BaseOutputParser):
    """
    Parses JSON output from LLM after removing markdown code fences or leading 'json' tags.
    """

    def parse(self, text: str, bypass: bool = False) -> List[Dict] | str:
        # Remove triple backtick blocks or leading 'json'
        cleaned_text = text.strip()

        # Remove markdown-style ```json ... ``` wrapping
        if cleaned_text.startswith("```json"):
            cleaned_text = re.sub(r"^```json\s*", "", cleaned_text)
        if cleaned_text.startswith("```"):
            cleaned_text = re.sub(r"^```", "", cleaned_text)
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3].strip()
        cleaned_text = re.sub(r'\\_', '_', cleaned_text)
        try:
            cleaned_text = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', cleaned_text)
            # remove only commas immediately before a closing ] or }
            cleaned_text = re.sub(r",\s*(?=[\]\}])", "", cleaned_text)

            if bypass:
                return cleaned_text
        except re.error as e:
            logger.error(f"Regex error while cleaning text: {e}")
        parsed = {}
        try:
            parsed = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON output: {e}\nCleaned text:\n{cleaned_text}")

        return parsed
