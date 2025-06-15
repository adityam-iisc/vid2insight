from dataclasses import dataclass, field

from agent.common.state.input_state import InputState


@dataclass(kw_only=True)
class AgentState(InputState):
    """Represents the  state for the agent."""


    cumulative_transcript: str = field(default=" ")

    intent: str = field(default="")

    exec_summary: str = field(default="")

    product_document: bool = field(default=False)

    mcq: str = field(default="")

    notes_summary:str = field(default="")

    answer: str = field(default="")
    """Final answer"""
