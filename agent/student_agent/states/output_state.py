from dataclasses import dataclass, field

from agent.common.state.input_state import InputState


@dataclass(kw_only=True)
class OutputState(InputState):
    """Represents the output state for the agent."""

    answer: str = field(default="")
    transcript: list[str] = field(default_factory=list)
    # Final answer
