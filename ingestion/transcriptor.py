import json

import cv2
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
import uuid
import re
import agent
from agent.config.initialize_logger import logger

from agent.config.assistant_config import AssistantConfiguration
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
import shutil
import os
import cv2
import base64
from typing import Dict, List, Union
from ingestion import prompts
from ingestion import constants


from ingestion.audio_extractor import VideoAudioProcessor
from ingestion.audio_transcript_generator import generate_audio_segment_transcript
from ingestion.frame_extractor import FrameExtractor
from ingestion.frame_json_parser import FrameJsonOutputParser
from ingestion.frame_transcript_generator import generate_frame_segment_transcript


def generate_transcript(video_path, path_to_folder, video_id) :
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
        logger.info("---GENERATE TRANSCRIPT FOR INGESTION---")

        configuration = AssistantConfiguration()
        logger.info(configuration.default_llm_model['provider'])
        logger.info(configuration.default_llm_model['model_name'])
        chat_model = configuration.get_model(configuration.default_llm_model)
        # Extract segments from the video and audio
        extract_segments(video_path, path_to_folder, video_id)
        output_list = llm_requests(chat_model, path_to_folder)
        json_str = json.dumps(output_list)
        with open(os.path.join(path_to_folder, 'transcript.json'), 'w') as f:
            f.write(json_str)

        # Clean up audio directory
        audio_directory = os.path.join(path_to_folder, "audio_segments")
        if os.path.exists(audio_directory):
            shutil.rmtree(audio_directory)
            print(f"{audio_directory} directory deleted")
        else:
            print(f"{audio_directory} directory does not exist")
        return output_list
    except Exception as exc:
        logger.exception(f"Exception in creating transcription of frame segments: {exc}")
        raise
def extract_segments(video_path: str, path_to_folder: str, video_id: str):
    """
    Extract segments from the video and audio.
    :param video_path: folder path to the video file
    :param path_to_folder: folder path to store the extracted segments
    :param video_id: unique identifier for the video
    :return:
    """
    SEGMENT_DURATION_SECONDS = 30
    MAX_FRAMES_PER_SEGMENT_FOR_LLM = 20
    SCENE_DETECTION_THRESHOLD = 27.0
    frame_extractor = FrameExtractor(video_path=video_path, persist=True,
                                     segment_duration_seconds=SEGMENT_DURATION_SECONDS,
                                     max_frames_per_segment=MAX_FRAMES_PER_SEGMENT_FOR_LLM,
                                     scene_detection_threshold=SCENE_DETECTION_THRESHOLD)
    segments_data = frame_extractor.extractor(video_id, mode=2)
    print("Frame processing completed")
    aob = VideoAudioProcessor(
        input_path=video_path,
        output_path=f"../docs/{video_id}/audio_segments/audio_output.wav",
        interval_s=30,
        persist=True
    )
    audio_chunks = aob.extractor()
def read_segments_from_folder(path_to_folder):
    """
    Read frames from a folder and convert them to base64 encoded strings.
    :param path_to_frame_folder: folder path containing frame segments
    :return: base 64 encoded strings of images in a dictionary
    """
    frame_directory = os.path.join(path_to_folder, "frames")
    audio_directory = os.path.join(path_to_folder, "audio_segments")
    base64_encoded_audios = read_audio_segs_from_folder(audio_directory)
    num_frame_dir = sum(1 for entry in os.scandir(frame_directory) if entry.is_dir())
    base64_encoded_images = []
    for idx in range(num_frame_dir):
        segment_id = f"{idx:03d}"
        frame_seg_directory = os.path.join(frame_directory, segment_id)
        current_seg = []
        for entry in os.scandir(frame_seg_directory):

            if entry.is_file():  # check if it's a file
                logger.info(entry.name)
                img_path = os.path.join(frame_seg_directory, entry.name)
                with open(f"{img_path}", "rb") as imagefile:
                    convert = base64.b64encode(imagefile.read()).decode('utf-8')
                current_seg.append(f"{convert}")
        logger.info(f"segment_id: {segment_id} len: {len(current_seg)}")
        base64_encoded_images.append(current_seg)
    logger.info(f"len: {len(base64_encoded_images)} {len(base64_encoded_audios)}" )
    return base64_encoded_audios, base64_encoded_images

def read_audio_segs_from_folder(path_to_folder) -> Dict[str, str]:
    directory = path_to_folder
    audio_base64 = []
    for entry in os.scandir(directory):
        if entry.is_file():  # check if it's a file
            logger.info(entry.name)
            audio_path = os.path.join(directory, entry.name)
            with open(f"{audio_path}", "rb") as audiofile:
                convert = base64.b64encode(audiofile.read()).decode('utf-8')
            audio_base64.append(f"{convert}")
    return audio_base64

def llm_requests(chat_model, path_to_folder):
    """
    Create a list of LLM requests from the base64 encoded images.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing image data for LLM requests.
    """



    # Read frames from the folder and convert to base64
    base64_audio, base64_img = read_segments_from_folder(path_to_folder) #"../docs/frames"
    req_output_list = []


    idx = 0
    for audio_seg, image_seg_list in zip(base64_audio, base64_img):
        req_parts = [{"type": "text", "text": prompts.FINAL_PROMPT}]
        logger.info("processing segment: %d", idx)
        idx += 1
        req_parts.append(
            {
                "type": "media",
                "data": audio_seg,
                "mime_type": "audio/wav",
            }
        )
        for image_seg in image_seg_list:
            req_parts.append(
                {
                    "type": "image",
                    "source_type": "base64",
                    "data": image_seg,
                    "mime_type": "image/jpeg",
                }
            )
        req_output = get_llm_response(req_parts, chat_model)
        req_output_list.append(req_output)

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
    frame_transcript = chat_model.invoke(messages)
    logger.debug(f"Generated transcript: {frame_transcript.content}")
    print(f"Generated transcript: {frame_transcript.content}")
    # Use the parser
    parser = FrameJsonOutputParser()

    parsed_output = parser.parse(frame_transcript.content)

    return parsed_output





def create_ingestion_data(video_path:str):
    video_id = uuid.uuid4()


    if os.path.isfile(video_path):
        print(f"{video_path} exists")
    else:
        print(f"{video_path} does not exist")

    path_to_folder = f"../docs/{str(video_id)}"
    os.makedirs(path_to_folder, exist_ok=True)
    generate_transcript(video_path, path_to_folder, str(video_id))

if __name__ == "__main__":
    # TODO: Update hardcoded path_to_frame_folder
    # video_path = f"../docs/videos/video1.mp4"
    video_path = f"../docs/videos/video1.mp4"

    create_ingestion_data(video_path)