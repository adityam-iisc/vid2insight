from dataclasses import dataclass, field
from agent.common.state.input_state import InputState


@dataclass(kw_only=True)
class AgentState(InputState):
    """Represents the  state for the agent."""

    answer: str = field(default="")

    generated_mcq: str = field(default="")

    generated_summary : str = field(default="")

    is_modification_required: bool = field(default=False)
    feedback: str = field(default="")
    turn: int = field(default=0)
    # Final answer
