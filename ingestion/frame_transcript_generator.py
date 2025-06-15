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


def generate_frame_segment_transcript(path_to_frame_folder: str) -> tuple[dict[str, str], dict[str, str]]:
    """
    Generate a frame transcript based on the agent's state and configuration.

    Args:
        config (RunnableConfig): The configuration for the runnable.

    Returns:
        Dict[str, str]: A dictionary containing the generated frame transcript and related messages.
    """

    try:
        if os.path.isdir(path_to_frame_folder):
            logger.info("directory exists")
        else:
            logger.error(f"Directory {path_to_frame_folder} does not exist.")
            raise FileNotFoundError(f"Directory {path_to_frame_folder} does not exist.")

        # LLM Configuration
        logger.info("---GENERATE FRAME TRANSCRIPT FOR INGESTION---")

        configuration = AssistantConfiguration()
        logger.info(configuration.default_llm_model['provider'])
        logger.info(configuration.default_llm_model['model_name'])
        chat_model = configuration.get_model(configuration.default_llm_model)
        req_output_list, img_path_list = llm_requests(chat_model, path_to_frame_folder)
        return req_output_list, img_path_list
    except Exception as exc:
        logger.exception(f"Exception in creating transcription of frame segments: {exc}")
        raise

def read_frames_from_folder(path_to_frame_folder) -> Dict[str, str]:
    directory = path_to_frame_folder
    num_frame_dir = sum(1 for entry in os.scandir(directory) if entry.is_dir())
    img_base64_dict = {}
    for idx in range(num_frame_dir):
        segment_id = f"{idx:03d}"
        frame_seg_directory = os.path.join(directory, segment_id)
        for entry in os.scandir(frame_seg_directory):
            if entry.is_file():  # check if it's a file
                logger.info(entry.name)
                img_path = os.path.join(frame_seg_directory, entry.name)
                with open(f"{img_path}", "rb") as imagefile:
                    convert = base64.b64encode(imagefile.read()).decode('utf-8')
                img_base64_dict[f"{segment_id}/{entry.name}"] = f"{convert}"
    return img_base64_dict

def llm_requests(chat_model, path_to_frame_folder):
    """
    Create a list of LLM requests from the base64 encoded images.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing image data for LLM requests.
    """
    req_output_list = []

    req_parts = [{"type": "text", "text": prompts.FRAME_EXTRACT_PROMPT}]
    current_payload_size = (
        len(json.dumps(req_parts).encode("utf-8")))

    # Read frames from the folder and convert to base64
    base64_img = read_frames_from_folder(path_to_frame_folder) #"../docs/frames"

    # Create LLM requests from the base64 images
    img_list, img_path_list = get_img_content_list(base64_img)

    is_llm_call_pending = False
    for img, img_name in zip(img_list, base64_img.keys()):
        path = img_name
        projected_size = current_payload_size + len(json.dumps(img).encode("utf-8"))
        if projected_size > constants.MAX_PAYLOAD_BYTES:
            logger.info(f"Batch {path} – would exceed 19 MB limit.")
            req_output = get_llm_response(req_parts, chat_model)
            for req_op in req_output:
                req_output_list.append(req_op)
            logger.info("Request parts sent to LLM: {}",len(req_output_list))
            is_llm_call_pending = False

            # Reset the request parts and add the new image
            logger.info("Resetting request parts for the next batch.")
            req_parts = {"type": "text", "text": prompts.FRAME_EXTRACT_PROMPT}
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
        for req_op in req_output:
            # print(req_op)
            req_output_list.append(req_op)
        logger.info("Request parts sent to LLM")


    return req_output_list, img_path_list



def get_llm_response(req_parts: List[Dict[str, str]], chat_model: BaseChatModel) -> list[dict]:
    # Prepare prompts and messages
    messages = [
        HumanMessage(content=[
            *req_parts  # Add all images as content parts
        ])
    ]
    # Generate the frame transcript
    frame_transcript = chat_model.invoke(messages)
    logger.debug(f"Generated frame transcript: {frame_transcript.content}")
    print(f"Generated frame transcript: {frame_transcript.content}")
    # Use the parser
    parser = FrameJsonOutputParser()

    parsed_output = parser.parse(frame_transcript.content)

    return parsed_output


def get_img_content_list(base64_img : Dict[str,str]):
    img_list = []
    img_path_list = []
    for key in base64_img:
        img_list.append(
            {
                "type": "image",
                "source_type": "base64",
                "data": base64_img[key],
                "mime_type": "image/jpeg",
            }
        )
        img_path_list.append(key)
    return img_list, img_path_list

# ============ Test Code ===============
# if __name__ == "__main__":
#     # TODO: Update hardcoded path_to_frame_folder
#     video_id = "1234"
#     path_to_frame_folder = f"../docs/{video_id}/frames"
#     generate_frame_segment_transcript(path_to_frame_folder)
