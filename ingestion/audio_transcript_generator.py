import json
import os
import base64
import time
from langchain_core.language_models import BaseChatModel
from agent.config.initialize_logger import logger

from agent.config.assistant_config import AssistantConfiguration
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage

from typing import Dict, List
from ingestion import prompts
from ingestion.frame_json_parser import FrameJsonOutputParser


def generate_audio_segment_transcript(path_to_folder: str) -> list[dict]:
    """
    Generate a frame transcript based on the agent's state and configuration.

    Args:
        path_to_folder (str): The path to the folder containing audio segments.

    Returns:
        list[dict]: A dictionary containing the generated frame transcript and related messages.
    """

    try:
        if os.path.isdir(path_to_folder):
            logger.info("directory exists")
        else:
            logger.error(f"Directory {path_to_folder} does not exist.")
            raise FileNotFoundError(f"Directory {path_to_folder} does not exist.")

        # LLM Configuration
        logger.info("---GENERATE AUDIO SEGMENT TRANSCRIPT FOR INGESTION---")
        audio_dict = read_audio_segs_from_folder(path_to_folder)
        configuration = AssistantConfiguration()
        chat_model = configuration.get_model(configuration.default_llm_model)
        req_output_list = llm_requests(chat_model, path_to_folder)
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
    req_parts = [prompts.AUDIO_EXTRACT_PROMPT]

    # Read frames from the folder and convert to base64
    audio_segments = read_audio_segs_from_folder(path_to_folder)

    # Create LLM requests from the base64 images

    for audio_f_name in sorted(audio_segments.keys()):
        audio_base64 = audio_segments.get(audio_f_name, '')
        req_parts.append(audio_base64)
        req_output = get_llm_response(req_parts, chat_model)
       #  time.sleep(6)  # Sleep to avoid rate limiting issues with the LLM
        req_output_list.append(req_output)
        req_parts = [prompts.AUDIO_EXTRACT_PROMPT]
    return req_output_list



def get_llm_response(req_parts: List[str], chat_model: BaseChatModel) -> list[dict]:
    """
      Generate a response from the LLM based on the provided request parts.
      :param req_parts:  list[dict[str, str] | dict[str, str | list]
      :param chat_model: BaseChatModel
      :return: list[dict] : List of dictionaries containing the LLM response.
    """
    # Prepare prompts and messages
    messages = [
        HumanMessage(content=[
            {
                "type": "text",
                "text": req_parts[0]
            },
            {
                "type": "media",
                "data": ' '.join(req_parts[1:]),
                "mime_type": 'audio/wav',
            }
        ])
    ]
    # Generate the frame transcript
    audio_transcript = chat_model.invoke(messages)
    # time.sleep(6)

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
    audio_list = []
    for key in list(sorted(base64_audio.keys())):
        audio_list.append(
            {
                "type": "media",
                "data": base64_audio[key],
                "mime_type": "audio/wav",
            }
        )
    return audio_list

# ============ Test Code ===============
# if __name__ == "__main__":
#     # TODO: Update hardcoded path_to_folder
#     video_id = "1234"
#     path_to_folder = f"../docs/{video_id}/audio_segments"
#     generate_audio_segment_transcript(path_to_folder)
