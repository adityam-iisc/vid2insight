from dataclasses import dataclass, field

from agent.doc_agent.state.input_state import InputState


@dataclass(kw_only=True)
class AgentState(InputState):
    """Represents the  state for the agent."""

    raw_transcript: str = field(default="")

    cumulative_transcript: str = field(default=" ")

    intent: str = field(default="")

    exec_summary: str = field(default="")

    product_document: bool = field(default=False)

    is_modification_required: bool = field(default=False)

    feedback:str = field(default="")

    turn:int  = field(default=0)

    answer: str = field(default="")
    """Final answer"""
