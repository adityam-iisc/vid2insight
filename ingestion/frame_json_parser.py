
from typing import List, Dict
from langchain_core.output_parsers import BaseOutputParser
import json
import re

class FrameJsonOutputParser(BaseOutputParser):
    """
    Parses JSON output from LLM after removing markdown code fences or leading 'json' tags.
    """

    def parse(self, text: str) -> List[Dict]:
        # Remove triple backtick blocks or leading 'json'
        cleaned_text = text.strip()

        # Remove markdown-style ```json ... ``` wrapping
        if cleaned_text.startswith("```json"):
            cleaned_text = re.sub(r"^```json\s*", "", cleaned_text)
        if cleaned_text.startswith("```"):
            cleaned_text = re.sub(r"^```", "", cleaned_text)
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3].strip()

        try:
            parsed = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON output: {e}\nCleaned text:\n{cleaned_text}")

        return parsed
