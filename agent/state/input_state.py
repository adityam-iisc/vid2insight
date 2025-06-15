from dataclasses import dataclass

from agent.common.state.input_state import InputState as BaseInputState


@dataclass(kw_only=True)
class InputState(BaseInputState):

    expert_preference: str = ""
    """
    The agent choice made by the user.
    """

