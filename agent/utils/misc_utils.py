from typing import Union

from agent.doc_agent.initialize_logger import logger
from agent.state.agent_state import AgentState as MainAgentState
from agent.student_agent.states.agent_state import AgentState as StudentAgentState
from agent.doc_agent.state.agent_state import AgentState as DocAgentState
from dataclasses import asdict


def _remove_agent_choice(state: Union[MainAgentState, StudentAgentState, DocAgentState]) -> Union[StudentAgentState, DocAgentState]:
    """
    Returns a copy of the state with agent_choice removed.
    Args:
        state (Union[MainAgentState, StudentAgentState, DocAgentState]): The agent state object.
    Returns:
        Union[StudentAgentState, DocAgentState]: A new AgentState object without the agent_choice field.
    Raises:
        Exception: If state cannot be converted or reconstructed.
    """
    try:
        state_dict = asdict(state)
        if 'agent_choice' in state_dict:
            logger.info("Removing 'agent_choice' from state.")
            state_dict.pop('agent_choice')
        else:
            logger.warning("'agent_choice' not found in state.")
        # Determine which AgentState class to use for reconstruction
        if isinstance(state, StudentAgentState):
            new_state = StudentAgentState(**state_dict)
        elif isinstance(state, DocAgentState):
            new_state = DocAgentState(**state_dict)
        else:
            logger.warning("Unknown AgentState type, returning as MainAgentState.")
            new_state = MainAgentState(**state_dict)
        logger.info("Successfully created AgentState without 'agent_choice'.")
        return new_state
    except Exception as e:
        logger.exception(f"Failed to remove 'agent_choice' from state: {e}")
        raise