import json

import cv2
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import Part

import re
import agent
from agent.config.initialize_logger import logger

from agent.config.assistant_config import AssistantConfiguration
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage

import os
import base64
from typing import Dict, List, Union
from ingestion import prompts
from ingestion import constants
from ingestion.frame_json_parser import FrameJsonOutputParser


def generate_segment_transcript(path_to_folder: str) -> list[dict]:
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


        configuration = AssistantConfiguration()
        logger.info(configuration.default_llm_model['provider'])
        logger.info(configuration.default_llm_model['model_name'])
        chat_model = configuration.get_model(configuration.default_llm_model)
        llm_requests(chat_model,path_to_folder)
    except Exception as exc:
        logger.exception(f"Exception in creating transcription of frame segments: {exc}")
        raise


def llm_requests(chat_model, path_to_folder: str) -> List[Dict[str, str]]:
    """
    Create a list of LLM requests from the base64 encoded images.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing image data for LLM requests.
    """
    req_output_list = []

    req_parts = [{"type": "text", "text": prompts.COMBINED_EXTRACT_PROMPT},
                 {"type": "list", "items": []}]
    current_payload_size = (
        len(json.dumps(req_parts).encode("utf-8")))


    # Create LLM requests from the base64 images
    content = get_content(path_to_folder)

    is_llm_call_pending = False
    for content_node in content["items"]:

        projected_size = current_payload_size + len(json.dumps(content_node).encode("utf-8"))
        if projected_size > constants.MAX_PAYLOAD_BYTES:
            logger.info(f"Batch payload – would exceed 19 MB limit.")
            req_output = get_llm_response(req_parts, chat_model)
            for req_op in req_output:
                req_output_list.append(req_op)
            logger.info("Request parts sent to LLM: {}",len(req_output_list))
            is_llm_call_pending = False
            content_node_list=[]

            # Reset the request parts and add the new image
            logger.info("Resetting request parts for the next batch.")
            req_parts = [{"type": "text", "text": prompts.COMBINED_EXTRACT_PROMPT},
                         {"type": "list", "items": []}]
            current_payload_size = (
                len(json.dumps(req_parts).encode("utf-8")))
            break
        else:
            is_llm_call_pending = True
            req_parts[1]["items"].append(content_node)
            current_payload_size = projected_size
            logger.info(f"Added payload – current payload size: {current_payload_size / (1024 * 1024):.2f} MB")
    logger.info(f"Final payload size: {current_payload_size / (1024 * 1024):.2f} MB")
    if is_llm_call_pending:
        logger.info("Sending final request parts to LLM.")
        req_output = get_llm_response(req_parts, chat_model)
        for req_op in req_output:
            # print(req_op)
            req_output_list.append(req_op)
        logger.info("Request parts sent to LLM")
    return req_output_list



def get_llm_response(req_parts, chat_model: BaseChatModel) -> list[dict]:
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


def get_content(path_to_folder: str) :
    audio_directory = os.path.join(path_to_folder, "audio_segments")
    frames_directory = os.path.join(path_to_folder, "frames")
    num_frame_dir = sum(1 for entry in os.scandir(frames_directory) if entry.is_dir())
    num_audio_files = sum(1 for entry in os.scandir(audio_directory) if entry.is_file())
    content = {
        "type": "list",
        "items":[]
    }
    for idx in range(num_frame_dir):
        content_list = []
        segment_id =f"{idx:03d}"
        audio_file_name = f"audio_output_{segment_id}.wav"
        audio_file_path = os.path.join(audio_directory, audio_file_name)
        with open(f"{audio_file_path}", "rb") as audiofile:
            audio_base62 = base64.b64encode(audiofile.read()).decode('utf-8')
        content_list.append({
            "type": "media",
            "data": audio_base62,
            "mime_type": "audio/wav"
        })
        frame_seg_directory = os.path.join(frames_directory, segment_id)
        for entry in os.scandir(frame_seg_directory):
            if entry.is_file():
                logger.info(entry.name)
                img_path = os.path.join(frame_seg_directory, entry.name)
                with open(f"{img_path}", "rb") as imagefile:
                    img_base64 = base64.b64encode(imagefile.read()).decode('utf-8')
                    content_list.append({
                        "type": "image",
                        "source_type": "base64",
                        "data": img_base64,
                        "mime_type": "image/jpeg",
                    })
        content["items"].append(content_list)
    return content





if __name__ == "__main__":
    # TODO: Update hardcoded path_to_frame_folder
    video_id = "1234"
    path_to_folder = f"../docs/{video_id}"
    generate_segment_transcript(path_to_folder)
