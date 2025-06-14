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


def generate_transcript(video_path: str, path_to_folder: str, video_id: str) -> list[dict]:
    """
    Generate a frame transcript based on the agent's state and configuration.

    Args:
        config (RunnableConfig): The configuration for the runnable.

    Returns:
        Dict[str, str]: A dictionary containing the generated frame transcript and related messages.
    """

    try:
        # LLM Configuration
        logger.info("---GENERATE AUDIO SEGMENT TRANSCRIPT FOR INGESTION---")
        configuration = AssistantConfiguration()
        logger.info(configuration.default_llm_model['provider'])
        logger.info(configuration.default_llm_model['model_name'])
        chat_model = configuration.get_model(configuration.default_llm_model)

        # extract segments from the video and audio
        extract_segments(video_path, path_to_folder, video_id)
        segment_transcripts = {}
        # generate audio segment transcript
        audio_directory = f"{path_to_folder}/audio_segments"
        audio_seg_transcripts = generate_audio_segment_transcript(audio_directory)
        for idx, audio_seg in enumerate(audio_seg_transcripts):
            segment_id = f"{idx:03d}"
            segment_transcripts[segment_id] = {
                "audio_transcript": audio_seg,
                "frame_transcript": [],
                "combined_transcript": ""
            }
        # generate frame segment transcript
        frame_directory = f"{path_to_folder}/frames"
        frame_seg_transcripts, img_path_list = generate_frame_segment_transcript(frame_directory)
        for frame_seg, img_path in zip(frame_seg_transcripts, img_path_list):
            segment_id = img_path.split('/')[0]
            frame_segment_directory = os.path.join(frame_directory, segment_id)
            segment_transcripts[segment_id]["frame_transcript"].append(frame_segment_directory)
        print("Segment processing completed")
        llm_requests(chat_model,segment_transcripts)
    except Exception as exc:
        logger.exception(f"Exception in creating transcription of frame segments: {exc}")
        raise

def extract_segments(video_path: str, path_to_folder: str, video_id: str):
    SEGMENT_DURATION_SECONDS = 15
    MAX_FRAMES_PER_SEGMENT_FOR_LLM = 10
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
        interval_s=15,
        persist=True
    )
    audio_chunks = aob.extractor()



def llm_requests(chat_model, segment_transcripts) -> List[Dict[str, str]]:
    """
    Create a list of LLM requests from the base64 encoded images.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing image data for LLM requests.
    """
    req_output_list = []

    req_parts = [{"type": "text", "text": prompts.AUDIO_EXTRACT_PROMPT_2} ]
    current_payload_size = (
        len(json.dumps(req_parts).encode("utf-8")))

    # Read frames from the folder and convert to base64
    base64_img = read_audio_segs_from_folder(path_to_frame_folder)

    # Create LLM requests from the base64 images
    img_list = get_audio_content_list(base64_img)

    is_llm_call_pending = True
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
            req_parts = {"type": "text", "text": prompts.AUDIO_EXTRACT_PROMPT_2}
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
    return req_output_list



def get_llm_response(req_parts: List[Dict[str, str]], chat_model: BaseChatModel) -> list[dict]:
    # Prepare prompts and messages
    messages = [
        HumanMessage(content=[
            *req_parts  # Add all images as content parts
        ])
    ]
    # Generate the frame transcript
    audio_transcript = chat_model.invoke(messages)
    # logger.debug(f"Generated audio transcript: {audio_transcript.content}")
    # print(f"Generated audio transcript: {audio_transcript.content}")
    # Use the parser
    parser = FrameJsonOutputParser()

    parsed_output = parser.parse(audio_transcript.content)

    # Access example
    # logger.info("Parsed Output: ", parsed_output)
    #logger.info("Summary Title: " ,parsed_output[0]["summary"]["title"])
    return parsed_output


def get_audio_content_list(base64_audio : Dict[str,str]):
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

if __name__ == "__main__":
    # TODO: Update hardcoded path_to_frame_folder
    video_id = uuid.uuid4()
    video_path = f"../docs/videos/video1.mp4"
    if os.path.isfile(video_path):
        print(f"{video_path} exists")
    else:
        print(f"{video_path} does not exist")
    path_to_folder = f"../docs/{video_id}"
    os.makedirs(os.path.dirname(path_to_folder), exist_ok=True)
    generate_transcript(video_path, path_to_folder, str(video_id))


