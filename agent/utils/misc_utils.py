from typing import Union

from agent.config.initialize_logger import logger
from agent.state.agent_state import AgentState as MainAgentState
from agent.student_agent.states.agent_state import AgentState as StudentAgentState
from agent.doc_agent.state.agent_state import AgentState as DocAgentState
from dataclasses import asdict


def _remove_agent_choice(state: Union[MainAgentState, StudentAgentState, DocAgentState, dict]) -> Union[StudentAgentState, DocAgentState]:
    """
    Returns a copy of the state with agent_choice removed.
    Accepts either a dataclass instance or a dict.
    """
    from dataclasses import is_dataclass
    try:
        if is_dataclass(state):
            state_dict = asdict(state)
        elif isinstance(state, dict):
            state_dict = dict(state)
        else:
            raise ValueError("State must be a dataclass or dict")
        if 'agent_choice' in state_dict:
            logger.info("Removing 'agent_choice' from state.")
            state_dict.pop('agent_choice')
        else:
            logger.warning("'agent_choice' not found in state.")
        # Try to detect which AgentState to use
        # Use 'frame_path' to detect StudentAgentState, 'exec_summary' for DocAgentState
        if 'frame_path' in state_dict:
            new_state = StudentAgentState(**state_dict)
        elif 'exec_summary' in state_dict or 'product_document' in state_dict:
            new_state = DocAgentState(**state_dict)
        else:
            logger.warning("Unknown AgentState type, returning as MainAgentState.")
            new_state = MainAgentState(**state_dict)
        logger.info("Successfully created AgentState without 'agent_choice'.")
        return new_state
    except Exception as e:
        logger.exception(f"Failed to remove 'agent_choice' from state: {e}")
        raise