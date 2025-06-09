from dataclasses import dataclass
from typing import Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


@dataclass(kw_only=True)
class InputState:
    """Represents the input state for the agent."""
    messages: Annotated[list[AnyMessage], add_messages]
    """Messages track the primary execution state of the agent."""




