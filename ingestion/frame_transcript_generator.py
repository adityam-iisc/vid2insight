import cv2
from langchain_core.runnables import RunnableConfig
from agent.config.initialize_logger import logger

from agent.config.assistant_config import AssistantConfiguration
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage

import os
import cv2
import base64
from typing import Dict, List, Union

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
        logger.info("---GENERATE FRAME TRANSCRIPT FOR INGESTION---")
        dict = read_frames_from_folder(path_to_frame_folder)
        llm_msg = request_llm(dict)
        configuration = AssistantConfiguration()
        logger.info(configuration.default_llm_model['provider'])
        logger.info(configuration.default_llm_model['model_name'])
        llm = configuration.get_model(configuration.default_llm_model)
        response = llm.invoke([llm_msg])
        print(response.text())

        # resp = llm.invoke("Hello, world!")
        # logger.info(resp)
        # messages = [
        #     SystemMessage(content=prompts.FRAME_TRANSCRIPT_PROMPT.format),
        #     HumanMessage(content="Generate a product document based on the provided transcript.")
        # ]
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
    img_list.append({"type": "text", "text": "Create transcript of the following images. Summarize the contect in each image."})
    for key in base64_img:
        img_list.append(
            {
                "type": "image",
                "source_type": "base64",
                "data": base64_img[key],
                "mime_type": "image/jpeg",
            }
        )
    message = {
        "role": "user",
        "content": img_list
    }
    return message

if __name__ == "__main__":
    # TODO: Update hardcoded path_to_frame_folder
    path_to_frame_folder = "../docs/frames"
    generate_frame_segment_transcript(path_to_frame_folder)
