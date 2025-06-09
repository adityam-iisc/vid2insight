from dataclasses import dataclass, field
from agent.doc_agent.state.input_state import InputState

@dataclass(kw_only=True)
class AgentState(InputState):
    """Represents the  state for the agent."""

    transcript: str = field(default="")

    intent: str = field(default="")

    frame_path: str = field(default="")

    answer: str = field(default="")
    """Final answer"""






