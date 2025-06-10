from dataclasses import dataclass, field
from agent.doc_agent.state.input_state import InputState

@dataclass(kw_only=True)
class AgentState(InputState):
    """Represents the  state for the agent."""


    raw_transcript: str = field(default="")

    intent: str = field(default="")

    exec_summary: str = field(default="")

    product_document: bool = field(default=False)

    # user_messages: str = field(default="")
    # """
    # Latest user messages in the conversation.
    # """


    answer: str = field(default="")
    """Final answer"""






