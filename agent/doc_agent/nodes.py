"""
Module: nodes.py
Description: Contains core node functions for the document agent, including transcript loading, product document generation, executive summary, intent decision, and chat response.
Implements world-class logging, type hints, exception handling, and docstring standards.
"""
from typing import Dict, List, Union

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage,AIMessage
from langchain_core.runnables import RunnableConfig

import raw_data
from agent.config.assistant_config import AssistantConfiguration
from agent.config.initialize_logger import logger
from agent.doc_agent import prompts, constants
from agent.doc_agent.state.agent_state import AgentState


def load_frame_transcript(state: AgentState, *, config: RunnableConfig) -> Dict[str, str]:
    """
    Load the frame transcript from the state.

    Args:
        state (AgentState): The current state of the agent.
        config (RunnableConfig): The configuration for the runnable.

    Returns:
        Dict[str, str]: A dictionary containing the frame transcript and intent.
    """
    try:
        logger.info("---LOADING FRAME TRANSCRIPT---")
        if state.cumulative_transcript == ' ':
            frame_transcript = raw_data.FRAME_DATA
            logger.debug(f"Loaded frame transcript: {frame_transcript}")
            intent = config['metadata'].get('intent', '')
            logger.debug(f"Intent from config: {intent}")
            configuration = AssistantConfiguration.from_runnable_config(config)
            chat_model = configuration.get_model(configuration.default_llm_model)
            # generate_cumulative_transcript =
            message = [
                SystemMessage(content=prompts.GENERATE_CUMULATIVE_TRANSCRIPT.format(context=frame_transcript)),
                HumanMessage(content="Generate a cumulative transcript based on the provided frame transcript.")
            ]
            response = chat_model.invoke(message)

            return {
                "raw_transcript": frame_transcript,
                "intent": intent,
                "cumulative_transcript": response.content
            }
        else:
            logger.info("everything is already loaded, skipping load_frame_transcript")
            return {
                "intent":config['metadata'].get('intent', '')

            }

    except Exception as exc:
        logger.exception(f"Exception in load_frame_transcript: {exc}")
        raise


def generate_product_document(state: AgentState, *, config: RunnableConfig) -> Dict[str, str]:
    """
    Generate a product document based on the agent's state and configuration.

    Args:
        state (AgentState): The current state of the agent.
        config (RunnableConfig): The configuration for the runnable.

    Returns:
        Dict[str, str]: A dictionary containing the generated product document and related messages.
    """
    try:
        logger.info("---GENERATE PRODUCT DOCUMENT---")
        configuration = AssistantConfiguration.from_runnable_config(config)
        chat_model = configuration.get_model(configuration.default_llm_model)
        # if state.feedback == '':
        #     messages = [
        #         SystemMessage(content=prompts.PRODUCT_DOCUMENT_PROMPTS.format(context=state.raw_transcript)),
        #     ] + state.messages[-1]
        # else:
        #     messages = [
        #         SystemMessage(content=prompts.PRODUCT_DOCUMENT_PROMPTS.format(context=state.raw_transcript)),
        #     ] + state.messages
        messages = [
            SystemMessage(content=prompts.PRODUCT_DOCUMENT_PROMPTS.format(context=state.cumulative_transcript)),
        ] + state.messages
        logger.debug(f"Messages for product document: {messages}")
        product_doc = chat_model.invoke(messages)
        logger.debug(f"Generated product document: {product_doc.content}")
        return {
            "product_document": product_doc.content,
            "messages": AIMessage(product_doc.content),
            'answer': product_doc.content
        }
    except Exception as exc:
        logger.exception(f"Exception in generate_product_document: {exc}")
        raise


def generate_executive_summary(state: AgentState, *, config: RunnableConfig) -> Dict[
    str, Union[BaseMessage, List[BaseMessage]]]:
    """
    Generate an executive summary based on the agent's state and configuration.

    Args:
        state (AgentState): The current state of the agent.
        config (RunnableConfig): The configuration for the runnable.

    Returns:
        Dict[str, Union[BaseMessage, List[BaseMessage]]]: A dictionary containing the generated executive summary and related messages.
    """
    try:
        logger.info("---GENERATE EXECUTIVE SUMMARY---")
        configuration = AssistantConfiguration.from_runnable_config(config)
        chat_model = configuration.get_model(configuration.default_llm_model)
        # if state.feedback == '':
        #     messages = [
        #         SystemMessage(content=prompts.EXECUTIVE_SUMMARY_PROMPT.format(context=state.raw_transcript)),
        #         HumanMessage(content="Generate an executive summary based on the provided transcript.")
        #     ]
        # else:
        #     messages = [
        #         SystemMessage(content=prompts.EXECUTIVE_SUMMARY_PROMPT.format(context=state.raw_transcript)),
        #         HumanMessage(content=f"Generate an executive summary based on the provided transcript and feedback: {state.feedback}")
        #     ] + state.messages
        # if len(state.messages) == 1:
        messages = [
            SystemMessage(content=prompts.EXECUTIVE_SUMMARY_PROMPT.format(context=state.cumulative_transcript)),
        ] + state.messages
        # else:
        #     messages = state.messages
        logger.debug(f"Messages for executive summary: {messages}")
        exec_summary = chat_model.invoke(messages)
        logger.debug(f"Generated executive summary: {exec_summary}")
        return {
            "exec_summary": exec_summary,
            "messages": exec_summary,
            'answer': exec_summary
        }
    except Exception as exc:
        logger.exception(f"Exception in generate_executive_summary: {exc}")
        raise


def decide_intent(state: AgentState, *, config: RunnableConfig) -> str:
    """
    Decide the intent based on the agent's state and configuration.

    Args:
        state (AgentState): The current state of the agent.
        config (RunnableConfig): The configuration for the runnable.

    Returns:
        str: The decided intent.

    Raises:
        ValueError: If the intent is not found in the state.
    """
    try:
        logger.debug("---DECIDE INTENT---")
        if hasattr(state, 'intent') and isinstance(state.intent, str) and state.intent.strip():
            logger.info(f"Intent found in state: {state.intent}")
            return state.intent
        else:
            logger.error("Intent not found in state")
            raise ValueError("Intent not found in state")
    except Exception as exc:
        logger.exception(f"Exception in decide_intent: {exc}")
        raise


def chat(state: AgentState, *, config: RunnableConfig) -> Dict[str, Union[str, List[str]]]:
    """
    Generate a response to the user's query based on the data.

    Args:
        state (AgentState): The current state of the agent, including retrieved documents and conversation history.
        config (RunnableConfig): The configuration for the runnable.

    Returns:
        Dict[str, Union[str, List[str]]]: A dictionary with a 'messages' key containing the generated response.
    """
    try:
        logger.debug("---CHAT---")
        configuration = AssistantConfiguration.from_runnable_config(config)
        chat_model = configuration.get_model(configuration.default_llm_model)
        # if hasattr(state, 'messages') and isinstance(state.messages, list) and len(state.messages) == 1:
        #     messages = [
        #                    SystemMessage(
        #                        content=prompts.CHAT_SYSTEM_PROMPT.format(context=state.raw_transcript)
        #                    )
        #                ] + state.messages
        # else:
        #     messages = state.messages if hasattr(state, 'messages') else []
        context = None
        if state.exec_summary != '':
            context = """
            Here is generated executive summary:
            """ + state.exec_summary.content
        elif state.product_document != '':
            context = """
            Here is generated product document:
            """ + state.product_document.content
        else:
            context = state.cumulative_transcript
        messages = [SystemMessage(content=prompts.CHAT_SYSTEM_PROMPT.format(context=context))
                           ] + state.messages
        logger.debug(f"Messages for chat: {messages}")
        response = chat_model.invoke(messages)
        logger.debug(f"Chat response: {response.content if hasattr(response, 'content') else response}")
        return {
            "messages": response.content if hasattr(response, 'content') else response,
            "answer": AIMessage(content=response.content)
        }
    except Exception as exc:
        logger.exception(f"Exception in chat: {exc}")
        raise


def evaluate(state: AgentState, *, config: RunnableConfig) -> Dict[str, str]:
    """
    Evaluate the agent's response based on the provided state and configuration.

    Args:
        state (AgentState): The current state of the agent.
        config (RunnableConfig): The configuration for the runnable.

    Returns:
        Dict[str, str]: A dictionary containing the evaluation result.
    """
    try:
        logger.info("---EVALUATE---")
        # Placeholder for evaluation logic
        configuration = AssistantConfiguration.from_runnable_config(config)
        chat_model = configuration.get_model(configuration.default_llm_model)
        chat_model_with_structure = chat_model.with_structured_output(constants.EvaluatorResponseModel)

        evaluation_data  = None
        if state.intent == constants.Intent.GENERATE_DOCS.value:
            evaluation_data= state.product_document
        elif state.intent == constants.Intent.GENERATE_EXEC_SUMMARY.value:
            evaluation_data = state.exec_summary
        else:
            raise ValueError(f"Unsupported intent for evaluation: {state.intent}")

        messages = [
            SystemMessage(content=prompts.EVALUATOR_PROMPT.format(context=evaluation_data))
        ] + state.messages
        response = chat_model_with_structure.invoke(messages)
        evaluation_result = "Evaluation completed successfully."
        logger.debug(f"Evaluation result: {evaluation_result}")
        return {
            "is_modification_required": response.is_modification_required,
            "feedback": response.feedback,
            "turn": state.turn +1,
            'answer': state.messages[-1],
            'messages': state.messages[-1]
        }
    except Exception as exc:
        logger.exception(f"Exception in evaluate: {exc}")
        raise


def decide_modification(state: AgentState, *, config: RunnableConfig) -> str:
    """
    Decide whether a modification is required based on the evaluation result.

    Args:
        state (AgentState): The current state of the agent.
        config (RunnableConfig): The configuration for the runnable.

    Returns:
        Dict[str, str]: A dictionary indicating whether a modification is required and the feedback.
    """
    try:
        logger.info("---DECIDE MODIFICATION---")
        if state.turn  >=3:
            logger.debug("Maximum turns reached, no modification required.")
            return 'end'
        elif state.is_modification_required:
            logger.debug("Modification is required based on evaluation.")
            return state.intent
        else:
            logger.debug("No modification required.")
            return 'end'
    except Exception as exc:
        logger.exception(f"Exception in decide_modification: {exc}")
        raise