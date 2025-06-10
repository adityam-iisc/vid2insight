from typing import Any

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

import raw_data
from agent.config.assistant_config import AssistantConfiguration
from agent.config.initialize_logger import logger
from agent.doc_agent.state.agent_state import AgentState
from agent.doc_agent import prompts


def load_frame_transcript(state: AgentState, *, config: RunnableConfig) -> dict[str, str]:
    """
    Load the frame transcript from the state.

    Args:
        args (tuple): A tuple containing the state, an unused parameter, and the config.

    Returns:
        dict[str, str]: A dictionary containing the frame path and transcript.
    """

    logger.info("---LOADING FRAME TRANSCRIPT---")
    # Todo: Read from the frame_transcript_path
    # For now, we will read hardcoded value
    frame_transcript = raw_data.FRAME_DATA
    return {
        "raw_transcript": frame_transcript,
        "intent": config['metadata']['intent']
    }

def generate_product_document(state: AgentState, *, config: RunnableConfig) -> dict[str, str]:
    """
    Generate a summary based on the agent's state and configuration.

    Args:
        state (AgentState): The current state of the agent.
        config (RunnableConfig): The configuration for the runnable.

    Returns:
        dict[str, str]: A dictionary containing the generated summary.
    """
    logger.info("---GENERATE SUMMARY---")

    configuration = AssistantConfiguration.from_runnable_config(config)
    chat_model = configuration.get_model(configuration.default_llm_model)
    messages = [
       SystemMessage(content=prompts.CHAT_SYSTEM_PROMPT.format(context=state.raw_transcript)),
        HumanMessage(content="Generate a product document based on the provided transcript.")
    ]
    product_doc = chat_model.invoke(messages)

    return {
        "product_document": product_doc.content,
        "messages": [product_doc.content],
        'answer': product_doc.content
    }



def generate_executive_summary(state: AgentState, *, config: RunnableConfig) -> dict[str, BaseMessage | list[BaseMessage]]:
    """
    Generate a multiple-choice question based on the agent's state and configuration.

    Args:
        state (AgentState): The current state of the agent.
        config (RunnableConfig): The configuration for the runnable.

    Returns:
        dict[str, str]: A dictionary containing the generated multiple-choice question.
    """
    logger.info("---GENERATE Executive Summary---")

    configuration = AssistantConfiguration.from_runnable_config(config)
    chat_model = configuration.get_model(configuration.default_llm_model)
    messages = [
        SystemMessage(content=prompts.EXECUTIVE_SUMMARY_PROMPT.format(context=state.raw_transcript)),
        HumanMessage(content="Generate an executive summary based on the provided transcript.")
    ]
    exec_summary = chat_model.invoke(messages)

    return {
        "exec_summary": exec_summary,
        "messages": [exec_summary],
        'answer': exec_summary
    }


def decide_intent(state: AgentState, *, config: RunnableConfig) -> str:
    """
    Decide the intent based on the agent's state and configuration.

    Args:
        state (AgentState): The current state of the agent.
        config (RunnableConfig): The configuration for the runnable.

    Returns:
        dict[str, str]: A dictionary containing the decided intent.

    Raises:
        ValueError: If the intent is not found in the state.
    """
    try:
        logger.debug("---DECIDE INTENT---")
        # Check if 'intent' is in the state
        if state.intent.lower() != '':
            return state.intent
        else:
            raise ValueError("Intent not found in state")
    except Exception as e:
        logger.exception(f"Error deciding intent: {e}", exc_info=True)
        raise

def chat(state: AgentState, *, config: RunnableConfig) -> dict[str, BaseMessage | list[BaseMessage]]:
    """
    Generate a response to the user's query based on the data.

    Args:
        state (AgentState): The current state of the agent, including retrieved documents and conversation history.
        config (RunnableConfig): The configuration for the runnable.

    Returns:
        dict[str, list[str]]: A dictionary with a 'messages' key containing the generated response.
    """
    logger.debug("---CHAT---")

    configuration = AssistantConfiguration.from_runnable_config(config)
    chat_model = configuration.get_model(configuration.default_llm_model)
    if len(state.messages) == 1:
        messages = [
            SystemMessage(
                content=prompts.CHAT_SYSTEM_PROMPT.format(context=state.raw_transcript)
            )
        ] + state.messages
    else:
        messages = [
              state.messages
        ]
    response = chat_model.invoke(messages)

    return {"messages": [response.content],
            "answer": response.content
            }