import json

import cv2
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableConfig

import re
import agent
from agent.config.initialize_logger import logger

from agent.config.assistant_config import AssistantConfiguration
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage

import os
import cv2
import base64
from typing import Dict, List, Union
from ingestion import prompts
from ingestion import constants
from ingestion.frame_json_parser import FrameJsonOutputParser


def generate_audio_segment_transcript(path_to_folder: str) -> list[dict]:
    """
    Generate a frame transcript based on the agent's state and configuration.

    Args:
        config (RunnableConfig): The configuration for the runnable.

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
        dict = read_audio_segs_from_folder(path_to_folder)
        llm_msg = get_audio_content_list(dict)
        configuration = AssistantConfiguration()
        logger.info(configuration.default_llm_model['provider'])
        logger.info(configuration.default_llm_model['model_name'])
        chat_model = configuration.get_model(configuration.default_llm_model)
        req_output_list = llm_requests(chat_model,path_to_folder)
        return req_output_list
    except Exception as exc:
        logger.exception(f"Exception in creating transcription of frame segments: {exc}")
        raise

def read_audio_segs_from_folder(path_to_folder) -> Dict[str, str]:
    directory = path_to_folder
    audio_base64_dict = {}
    for entry in os.scandir(directory):
        if entry.is_file():  # check if it's a file
            logger.info(entry.name)
            audio_path = os.path.join(directory, entry.name)
            with open(f"{audio_path}", "rb") as audiofile:
                convert = base64.b64encode(audiofile.read()).decode('utf-8')
            audio_base64_dict[f"{entry.name}"] = f"{convert}"
    return audio_base64_dict

def llm_requests(chat_model, path_to_folder: str) -> List[Dict[str, str]]:
    """
    Create a list of LLM requests from the base64 encoded images.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing image data for LLM requests.
    """
    req_output_list = []

    req_parts = [{"type": "text", "text": prompts.AUDIO_EXTRACT_PROMPT}]
    current_payload_size = (
        len(json.dumps(req_parts).encode("utf-8")))

    # Read frames from the folder and convert to base64
    base64_img = read_audio_segs_from_folder(path_to_folder)

    # Create LLM requests from the base64 images
    img_list = get_audio_content_list(base64_img)

    is_llm_call_pending = False
    for img, img_name in zip(img_list, base64_img.keys()):
        path = img_name
        projected_size = current_payload_size + len(json.dumps(img).encode("utf-8"))
        if projected_size > constants.MAX_PAYLOAD_BYTES:
            logger.info(f"Batch {path} – would exceed {constants.MAX_PAYLOAD_MB} MB limit.")
            req_output = get_llm_response(req_parts, chat_model)
            for req_op in req_output:
                req_output_list.append(req_op)
            logger.info("Request parts sent to LLM: {}",len(req_output_list))
            is_llm_call_pending = False

            # Reset the request parts and add the new image
            logger.info("Resetting request parts for the next batch.")
            req_parts = {"type": "text", "text": prompts.AUDIO_EXTRACT_PROMPT}
            current_payload_size = (
                len(json.dumps(req_parts).encode("utf-8")))
            break
        else:
            is_llm_call_pending = True
            req_parts.append(img)
            current_payload_size = projected_size
            logger.info(f"Added {path} – current payload size: {current_payload_size / (1024 * 1024):.2f} MB")
    logger.info(f"Final payload size: {current_payload_size / (1024 * 1024):.2f} MB")
    if is_llm_call_pending:
        logger.info("Sending final request parts to LLM.")
        req_output = get_llm_response(req_parts, chat_model)
        for req_op in req_output["segments"]:
            # print(req_op)
            req_output_list.append(req_op)
        logger.info("Request parts sent to LLM")
    return req_output_list



def get_llm_response(req_parts: List[Dict[str, str]], chat_model: BaseChatModel) -> list[dict]:
    """
          Generate a response from the LLM based on the provided request parts.
          :param req_parts:  list[dict[str, str] | dict[str, str | list]
          :param chat_model: BaseChatModel
          :return: list[dict] : List of dictionaries containing the LLM response.
    """
    # Prepare prompts and messages
    messages = [
        HumanMessage(content=[
            *req_parts  # Add all images as content parts
        ])
    ]
    # Generate the frame transcript
    audio_transcript = chat_model.invoke(messages)

    # Parse it and return it
    parser = FrameJsonOutputParser()
    parsed_output = parser.parse(audio_transcript.content)
    return parsed_output


def get_audio_content_list(base64_audio : Dict[str,str]):
    """
    Create a list of audio content dictionaries from the base64 encoded audio data.
    :param base64_audio: folder path to the audio segments
    :return: base64 encoded audio content list for LLM requests
    """
    img_list = []
    for key in base64_audio:
        img_list.append(
            {
                "type": "media",

                "data": base64_audio[key],
                "mime_type": "audio/wav",
            }
        )
    return img_list

# ============ Test Code ===============
# if __name__ == "__main__":
#     # TODO: Update hardcoded path_to_folder
#     video_id = "1234"
#     path_to_folder = f"../docs/{video_id}/audio_segments"
#     generate_audio_segment_transcript(path_to_folder)
