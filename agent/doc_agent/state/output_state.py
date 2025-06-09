from agent.doc_agent.state.input_state import InputState

from dataclasses import dataclass, field
@dataclass(kw_only=True)
class OutputState(InputState):
    """Represents the output state for the agent."""

    answer: str = field(default="")
    transcript: list[str] = field(default_factory=list)
    """Final answer"""




