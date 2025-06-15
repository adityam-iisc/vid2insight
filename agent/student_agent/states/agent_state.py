from dataclasses import dataclass, field
from agent.student_agent.states.input_state import InputState


@dataclass(kw_only=True)
class AgentState(InputState):
    """Represents the  state for the agent."""

    transcript: str = field(default="")
    cumulative_transcript: str = field(default=" ")
    intent: str = field(default="")
    frame_path: str = field(default="")
    answer: str = field(default="")
    is_modification_required: bool = field(default=False)
    feedback: str = field(default="")
    turn: int = field(default=0)
    # Final answer
