from typing import Dict
import json

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig

from agent.config.assistant_config import AssistantConfiguration
from agent.student_agent.constants import MCQResponseModel, SummaryResponseModel
from agent.student_agent.states.agent_state import AgentState
from agent.student_agent import prompts, constants
from agent.config.initialize_logger import logger

from dotenv import load_dotenv

load_dotenv('...')


def initialize_context(state: AgentState, *, config: RunnableConfig) -> Dict[str, str]:
    """
    Load the frame transcript from the state.

    Args:
        state (AgentState): The current state of the agent.
        config (RunnableConfig): The configuration for the runnable.

    Returns:
        Dict[str, str]: A dictionary containing the frame transcript and intent.
    """
    try:
        logger.info("---initialize context---")

        """
        making it dummy as logic got changed will re-use it for further enhancement where I need to get some extra information
        when we add some extra functionality like generating PPT etc 

        """
        # if state.context == ' ':
        #     frame_transcript =
        #     logger.debug(f"Loaded frame transcript: {frame_transcript}")
        #     intent = config['metadata'].get('intent', '')
        #     logger.debug(f"Intent from config: {intent}")
        #     configuration = AssistantConfiguration.from_runnable_config(config)
        #     chat_model = configuration.get_model(configuration.default_llm_model)
        #     # generate_cumulative_transcript =
        #     message = [
        #         SystemMessage(content=prompts.GENERATE_CUMULATIVE_TRANSCRIPT.format(context=frame_transcript)),
        #         HumanMessage(content="Generate a cumulative transcript based on the provided frame transcript.")
        #     ]
        #     response = chat_model.invoke(message)
        #
        #     return {
        #         "raw_transcript": frame_transcript,
        #         "intent": intent,
        #         "cumulative_transcript": response.content
        #     }
        # else:
        #     logger.info("everything is already loaded, skipping load_frame_transcript")
        #     return {
        #         "intent":config['metadata'].get('intent', '')
        #
        #     }
        if state.intent not in [e.value for e in constants.Intent]:
            logger.error(f"Invalid intent: {state.intent}. Must be one of {list(constants.Intent)}.")
            raise ValueError(f"Invalid intent: {state.intent}. Must be one of {list(constants.Intent)}.")
        # Redundant intent not required will remove in next iteration
        return {
            "intent": state.intent,
        }
    except Exception as exc:
        logger.exception(f"Exception in load_frame_transcript: {exc}")
        raise


def generate_mcq(state: AgentState, *, config: RunnableConfig) -> dict[str, str]:
    """
    Generate multiple-choice questions based on the agent's state and configuration.

    Args:
        state (AgentState): The current state of the agent.
        config (RunnableConfig): The configuration for the runnable.

    Returns:
        dict[str, str]: A dictionary containing the generated multiple-choice questions.
    """
    logger.info("---GENERATE MCQ---")

    cfg = AssistantConfiguration.from_runnable_config(config)
    chat_model = cfg.get_model(cfg.default_llm_model)
    additional_messages = state.messages if state.messages[-1] else ''
    cleaned_transcript = state.video_context.replace("\n", "").replace(" ", "")
    cleaned_transcript = " ".join(cleaned_transcript.split())
    messages = [
        SystemMessage(content=prompts.MCQ_GENERATOR_PROMPTS.replace("{context}", cleaned_transcript)),
        HumanMessage(
            content=f"Generate multiple-choice questions based on the provided transcript and on the following custom message {additional_messages}")
    ]
    mcq_doc = chat_model.invoke(messages)

    return {
        "mcq": mcq_doc.content,
        "answer": mcq_doc.content,
        "messages": AIMessage(mcq_doc.content)
    }


def generate_summary(state: AgentState, *, config: RunnableConfig) -> dict[str, str | SummaryResponseModel]:
    """
    Generate a student focussed summary based on the agent's state and configuration.
    :param state: Current state of the agent, including retrieved documents and conversation history.
    :param config: additional configuration for the runnable.
    :return: Output in the form of a dictionary containing the generated summary.
    """
    logger.info("---GENERATING STUDENT SUMMARY---")

    cfg = AssistantConfiguration.from_runnable_config(config)
    chat_model = cfg.get_model(cfg.default_llm_model)
    cleaned_transcript = state.video_context.replace("\n", "").replace(" ", "")
    cleaned_transcript = " ".join(cleaned_transcript.split())
    additional_messages = state.messages if state.messages[-1] else ''
    messages = [
        SystemMessage(content=prompts.STUDENT_SUMMARY_PLAN.replace("{context}", cleaned_transcript)),
        HumanMessage(content="Generate a student summary and plan on the provided transcript")
    ]
    summary_plan = chat_model.invoke(messages)

    return {
        "summary": summary_plan.content,
        "answer": summary_plan.content,
        "messages": AIMessage(summary_plan.content)
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
    cleaned_transcript = state.video_context.replace("\n", "").replace(" ", "")
    cleaned_transcript = " ".join(cleaned_transcript.split())
    if len(state.messages) == 1:
        messages = [
                       SystemMessage(
                           content=prompts.CHAT_SYSTEM_PROMPT.replace("{context}", cleaned_transcript)
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


def evaluate(state: AgentState, *, config: RunnableConfig) -> Dict[str, str | int]:
    """
    Evaluate the last response and decide if modification is required.
    """
    try:
        logger.info("---EVALUATE---")
        cfg = AssistantConfiguration.from_runnable_config(config)
        chat_model = cfg.get_model(cfg.default_llm_model).with_structured_output(constants.EvaluatorResponseModel)

        if state.intent == constants.Intent.GENERATE_MCQ.value:
            data = state.answer
        elif state.intent == constants.Intent.GENERATE_SUMMARY.value:
            data = state.answer
        else:
            raise ValueError(f"Unsupported intent for evaluation: {state.intent}")

        messages = [SystemMessage(content=prompts.EVALUATOR_PROMPT.replace("{context}", data))] + state.messages
        response = chat_model.invoke(messages)

        return {
            "is_modification_required": response.is_modification_required,
            "feedback": response.feedback,
            "turn": state.turn + 1,
            "answer": state.messages[-1],
            "messages": HumanMessage(f"feedback: {response.feedback}")
        }
    except Exception as exc:
        logger.exception(f"Exception in evaluate: {exc}")
        raise


def decide_modification(state: AgentState, *, config: RunnableConfig) -> str:
    """
    Decide whether to loop back for another modification or end.
    """
    try:
        logger.info("---DECIDE MODIFICATION---")
        if state.turn >= 3:
            return constants.Routes.END.value
        if state.is_modification_required:
            return state.intent
        return constants.Routes.END.value
    except Exception as exc:
        logger.exception(f"Exception in decide_modification: {exc}")
        raise
