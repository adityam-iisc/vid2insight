import cv2
from langchain_core.runnables import RunnableConfig
from agent.config.initialize_logger import logger

from agent.config.assistant_config import AssistantConfiguration
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage

import os
import cv2
import base64
from typing import Dict, List, Union
from agent.doc_agent import prompts
from ingestion.frame_json_parser import FrameJsonOutputParser


def generate_frame_segment_transcript(path_to_frame_folder: str): #-> Dict[str, str]:
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
        dict = read_frames_from_folder(path_to_frame_folder)
        llm_msg = request_llm(dict)
        configuration = AssistantConfiguration()
        logger.info(configuration.default_llm_model['provider'])
        logger.info(configuration.default_llm_model['model_name'])
        chat_model = configuration.get_model(configuration.default_llm_model)

        # Prepare prompts and messages
        messages = [
            HumanMessage(content=[
                {"type": "text", "text": prompts.FRAME_EXTRACT_PROMPT_2},
                *llm_msg  # Add all images as content parts
            ])
        ]

        # Generate the frame transcript
        frame_transcript = chat_model.invoke(messages)
        #logger.debug(f"Generated frame transcript: {frame_transcript.content}")

        # Use the parser
        parser = FrameJsonOutputParser()
        parsed_output = parser.parse(frame_transcript.content)

        # Access example
        print(parsed_output[0]["summary"]["title"])

    except Exception as exc:
        logger.exception(f"Exception in creating transcription of frame segments: {exc}")
        raise

def read_frames_from_folder(path_to_frame_folder) -> Dict[str, str]:
    directory = path_to_frame_folder
    img_base64_dict = {}
    for entry in os.scandir(directory):
        if entry.is_file():  # check if it's a file
            print(entry.name)
            img_path = os.path.join(directory, entry.name)
            with open(f"{img_path}", "rb") as imagefile:
                convert = base64.b64encode(imagefile.read()).decode('utf-8')
            img_base64_dict[f"{entry.name}"] = f"{convert}"
    return img_base64_dict

def request_llm(base64_img : Dict[str,str]):
    img_list = []
    for key in base64_img:
        img_list.append(
            {
                "type": "image",
                "source_type": "base64",
                "data": base64_img[key],
                "mime_type": "image/jpeg",
            }
        )
    return img_list

if __name__ == "__main__":
    # TODO: Update hardcoded path_to_frame_folder
    path_to_frame_folder = "../docs/frames"
    generate_frame_segment_transcript(path_to_frame_folder)
