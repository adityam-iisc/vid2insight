import json

from langchain_core.language_models import BaseChatModel
from agent.config.initialize_logger import logger
from agent.config.assistant_config import AssistantConfiguration
from langchain_core.messages import HumanMessage

import os
from typing import Dict, List
from ingestion import prompts
from ingestion.frame_json_parser import FrameJsonOutputParser


def generate_segment_transcript(path_to_folder: str) -> list[dict]:
    """
    Generate a frame transcript based on the agent's state and configuration.

    Args:
        path_to_folder (str): The path to the folder containing audio segments.

    Returns:
        Dict[str, str]: A dictionary containing the generated frame transcript and related messages.
    """

    try:
        if os.path.isdir(path_to_folder):
            logger.info("directory exists")
        else:
            logger.error(f"Directory {path_to_folder} does not exist.")
            raise FileNotFoundError(f"Directory {path_to_folder} does not exist.")

        # LLM Configuration
        logger.info("---GENERATE AUDIO SEGMENT TRANSCRIPT FOR INGESTION---")

        configuration = AssistantConfiguration()
        chat_model = configuration.get_model(configuration.default_llm_model)
        return llm_requests(chat_model, path_to_folder)
    except Exception as exc:
        logger.exception(f"Exception in creating transcription of frame segments: {exc}")
        raise


def llm_requests(chat_model, total_payload: dict) -> List[Dict[str, str]]:
    """
    Create a list of LLM requests from the base64 encoded images.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing image data for LLM requests.
    """
    req_output_list = []

    req_parts = [prompts.COMBINED_EXTRACT_PROMPT]

    content = get_content(total_payload)
    req_output = get_llm_response(req_parts, chat_model)
    return req_output_list



def get_llm_response(req_parts, chat_model: BaseChatModel) -> list[dict]:
    """
    Generate a response from the LLM based on the provided request parts.
    :param req_parts:  list[dict[str, str] | dict[str, str | list]
    :param chat_model: BaseChatModel
    :return: list[dict] : List of dictionaries containing the LLM response.
    """
    print("Generating LLM response...")
    # Prepare prompts and messages
    messages = [
        HumanMessage(content=req_parts)
    ]
    # Generate the frame transcript
    transcript = chat_model.invoke(messages)
    # logger.debug(f"Generated audio transcript: {audio_transcript.content}")
    # print(f"Generated audio transcript: {audio_transcript.content}")
    # Use the parser
    parser = FrameJsonOutputParser()

    parsed_output = parser.parse(transcript.content)

    # Access example
    logger.info("Parsed Output: ", parsed_output)
    #logger.info("Summary Title: " ,parsed_output[0]["summary"]["title"])
    return parsed_output


def get_content(content: list):
    """

    :param content:
    :return:
    """
    content = [
    (
        "system",
        content[0]
    ),
        ("human", content[1]),
    ]

    return content





# if __name__ == "__main__":
#     # TODO: Update hardcoded path_to_frame_folder
#     video_id = ""
#     path_to_folder = f"../docs/"
#     generate_segment_transcript(path_to_folder)
