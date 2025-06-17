from typing import Any, Dict

from langchain.chains.question_answering.map_reduce_prompt import messages
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from agent.config.assistant_config import AssistantConfiguration
from agent.config.initialize_logger import logger
from agent.state.agent_state import AgentState
from agent import constants, prompts
from agent.utils.misc_utils import _remove_agent_choice

from agent.constants import AgentType




def agent_router(state: AgentState, *, config: RunnableConfig) -> dict[str, str]:
    """
    Routes the agent based on the agent_choice in the state.
    Raises ValueError if agent_choice is not a valid AgentType.
    Args:
        state (AgentState): The current state of the agent.
        config (RunnableConfig): The configuration for the agent.
    Returns:
        str: The value of the agent_choice if valid.
    """

    try:
        return config['metadata']['agent_choice']
        agent_choice = state.agent_choice
        if agent_choice not in [e.value for e in AgentType]:
            logger.error(f"Invalid agent_choice: {agent_choice}")
            raise ValueError(f"Invalid agent_choice: {agent_choice}")
        logger.info(f"Routing to agent: {agent_choice}")
        return agent_choice
    except Exception as e:
        logger.exception(f"Exception in agent_router: {e}")
        raise

def student_subgraph(state: AgentState, *, config: RunnableConfig) -> Any:
    """
    Handles the student agent's subgraph.
    Args:
        state (AgentState): The current state of the agent.
        config (RunnableConfig): The configuration for the agent.
    Returns:
        Any: The result of the student agent's subgraph.
    """
    from agent.student_agent.student_graph import app
    try:
        logger.info("Invoking student_subgraph")
        # state_wo_choice = _remove_agent_choice(state)
        state_wo_choice = state
        result = app.invoke(state_wo_choice, config=config)
        logger.info("student_subgraph executed successfully")
        return result
    except Exception as e:
        logger.exception(f"Exception in student_subgraph: {e}")
        raise

def doc_subgraph(state: AgentState, *, config: RunnableConfig) -> Any:
    """
    Handles the document agent's subgraph.
    Args:
        state (AgentState): The current state of the agent.
        config (RunnableConfig): The configuration for the agent.
    Returns:
        Any: The result of the document agent's subgraph.
    """
    from agent.doc_agent.doc_graph import app
    try:
        logger.info("Invoking doc_subgraph")
        # state_wo_choice = _remove_agent_choice(state)
        state_wo_choice = state
        result = app.invoke(state_wo_choice, config=config)
        logger.info("doc_subgraph executed successfully")
        return result
    except Exception as e:
        logger.exception(f"Exception in doc_subgraph: {e}")
        raise

def format_response(state: AgentState, *, config: RunnableConfig) -> Dict[str, Any]:
    """
    Formats the response based on the agent type.
    Args:
        state (AgentState): The current state of the agent.
        config (RunnableConfig): The configuration for the agent.
    Returns:
        str: The formatted response.
    """
    try:
        logger.info("--------Formatting response--------")
        configuration = AssistantConfiguration.from_runnable_config(config)
        chat_model = configuration.get_model(configuration.default_llm_model)
        chat_model_with_structure = chat_model.with_structured_output(constants.AgentResponseModel)
        messages = [
            SystemMessage(content=prompts.RESPONSE_FORMAT),
            HumanMessage(content=state.answer)
        ]
        logger.info("Formatting response with chat model")
        response = chat_model_with_structure.invoke(messages)
        return {
            'chat_content': response.chat_content,
            'doc_content': response.doc_content or "",
            'messages': messages
        }
    except Exception as e:
        logger.exception(f"Exception in format_response: {e}")
        raise

def chat(state: AgentState, *, config: RunnableConfig) -> Dict[str, str]:
    """
    Handles the chat functionality of the agent.
    Args:
        state (AgentState): The current state of the agent.
        config (RunnableConfig): The configuration for the agent.
    Returns:
        Dict[str, str]: The chat response.
    """
    try:
        logger.info("--------Chatting with the agent--------")
        configuration = AssistantConfiguration.from_runnable_config(config)
        chat_model = configuration.get_model(configuration.default_llm_model)
        messages = [
            SystemMessage(content=prompts.CHAT_PROMPT.format(context=state.video_context)),
        ] + state.messages
        logger.info("Invoking chat model")
        response = chat_model.invoke(messages)
        return {'answer': response.content}
    except Exception as e:
        logger.exception(f"Exception in chat: {e}")
        raise