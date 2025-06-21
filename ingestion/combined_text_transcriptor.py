import json
import shutil

from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableConfig

from agent.config.initialize_logger import logger

from agent.config.assistant_config import AssistantConfiguration

import os
from typing import Dict, List
from ingestion import prompts
from ingestion.audio_extractor import VideoAudioProcessor
from ingestion.audio_transcript_generator import generate_audio_segment_transcript
from ingestion.frame_extractor import FrameExtractor
from ingestion.frame_json_parser import FrameJsonOutputParser
from ingestion.frame_transcript_generator import generate_frame_segment_transcript


def generate_transcript(video_path: str, output_dir: str, segment_duration: int) -> tuple[str, str]:
    """
    Generate a frame transcript based on the agent's state and configuration.

    Args:
        config (RunnableConfig): The configuration for the runnable.

    Returns:
        :param output_dir:
        :param video_path:
        :param segment_duration:
    """

    try:
        # LLM Configuration
        logger.info("---GENERATE SEGMENT TRANSCRIPT FOR INGESTION---")
        configuration = AssistantConfiguration()
        logger.info(configuration.default_llm_model['provider'])
        logger.info(configuration.default_llm_model['model_name'])
        chat_model = configuration.get_model(configuration.default_llm_model)

        # Extract segments from the video and audio
        extract_segments(video_path, output_dir, segment_duration)
        segment_transcripts = {}
        # Generate audio segment transcript
        audio_directory = os.path.join(output_dir, 'audio_segments')
        audio_seg_transcripts = generate_audio_segment_transcript(audio_directory)
        for idx, audio_seg in enumerate(audio_seg_transcripts):
            segment_id = f"{idx:03d}"
            segment_transcripts[segment_id] = {
                "audio_transcript": audio_seg,
                "frame_transcript": {}
            }
        # Generate frame segment transcript
        frame_directory = os.path.join(output_dir, "frames")
        frame_seg_transcripts = generate_frame_segment_transcript(frame_directory)
        for frame_seg in frame_seg_transcripts:
            img_path = frame_seg['title']
            segment_id = img_path.split('/')[0]
            if segment_transcripts.get(segment_id).get('frame_transcript'):
                frame_tx = segment_transcripts[segment_id]['frame_transcript']
                frame_tx['title'].append(frame_seg['title'])
                frame_tx['details'].append(frame_seg['explanation'])
            else:
                segment_transcripts.get(segment_id)['frame_transcript'] = {'title': [frame_seg['title']],
                                                                           'details': [frame_seg['explanation']]}

        logger.info("Segment processing completed")

        # Call LLM to combine audio and frame transcripts
        transcript = llm_requests(chat_model, segment_transcripts)
        segment_transcripts['combined_transcript'] = [transcript]
        json_str = json.dumps(segment_transcripts)
        with open(os.path.join(output_dir, 'transcript.json'), 'w') as f:
            f.write(json_str)

        # Clean up audio directory
        if os.path.exists(audio_directory):
            shutil.rmtree(audio_directory)
            print(f"{audio_directory} directory deleted")
        else:
            print(f"{audio_directory} directory does not exist")



    except Exception as exc:
        logger.exception(f"Exception in creating transcription of frame segments: {exc}")
        raise
    return json_str, output_dir


def extract_segments(video_path: str, output_dir: str, segment_duration: int):
    """
    Extract segments from the video and audio.
    :param video_path: Path to the input video file.
    :param output_dir: Path to the output directory where segments will be stored.
    :param segment_duration: Each segment's duration in seconds(input by user).
    :return: None
    """
    SEGMENT_DURATION_SECONDS = segment_duration
    MAX_FRAMES_PER_SEGMENT_FOR_LLM = 10
    SCENE_DETECTION_THRESHOLD = 27.0
    video_output_dir = os.path.join(output_dir, "frames")
    audio_output_dir = os.path.join(output_dir, "audio_segments")
    frame_extractor = FrameExtractor(video_path=video_path, persist=True,
                                     segment_duration_seconds=SEGMENT_DURATION_SECONDS,
                                     max_frames_per_segment=MAX_FRAMES_PER_SEGMENT_FOR_LLM,
                                     scene_detection_threshold=SCENE_DETECTION_THRESHOLD,
                                     frame_path=video_output_dir)
    segments_data = frame_extractor.extractor(mode=2)
    aob = VideoAudioProcessor(
        input_path=video_path,
        output_path=audio_output_dir,
        interval_s=segment_duration,
        persist=True
    )
    audio_chunks = aob.extractor()


def llm_requests(chat_model, segment_transcripts: dict) -> List[Dict[str, str]]:
    """
    Create a list of LLM requests from the base64 encoded images.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing image data for LLM requests.
    """

    req_parts = [prompts.COMBINED_EXTRACT_PROMPT]

    result: dict = {}
    for segment_id, segment_data in segment_transcripts.items():
        audio = segment_data.get("audio_transcript", {})
        details = segment_data.get("frame_transcript", {}).get("details", [])
        result[segment_id] = {
            "audio_transcript": audio,
            "frame_transcript": details
        }
    req_parts.append(json.dumps(result))

    req_output = get_llm_response(req_parts, chat_model)

    return req_output


def get_llm_response(req_parts, chat_model: BaseChatModel) -> list[dict]:
    """
      Generate a response from the LLM based on the provided request parts.
      :param req_parts:  list[dict[str, str] | dict[str, str | list]
      :param chat_model: BaseChatModel
      :return: list[dict] : List of dictionaries containing the LLM response.
      """
    # Prepare prompts and messages
    messages = [
        (
            'system',
            req_parts[0]
        ),
        ('human',
         req_parts[1])
        ]
    transcript = chat_model.invoke(messages)
    parser = FrameJsonOutputParser()
    parsed_output = parser.parse(transcript.content)
    return parsed_output


# ============ Test Code ===============

def create_ingestion_data(video_path, output_dir: str, segment_duration_seconds: int = 15) -> tuple[str, str]:
    try:
        if os.path.isfile(video_path):
            print(f"{video_path} exists")
        else:
            print(f"{video_path} does not exist")

        return generate_transcript(video_path, output_dir, segment_duration_seconds)
    except Exception as e:
        logger.exception(e)
        return '', ''


# if __name__ == "__main__":
#     # TODO: Update hardcoded path_to_frame_folder
#     # video_path = f"../docs/videos/video1.mp4"
#     video_path = f"/Users/admukhop/Desktop/iisc/Deep Learning/project/vid2insight/docs/input/aa4b9c4e5a905f6b941902ec971a9f55a76fb50aa61b05db641f37536357854d.mp4"
#
#     create_ingestion_data(video_path,
#                           output_dir='/Users/admukhop/Desktop/iisc/Deep Learning/project/vid2insight/docs/testing',
#                           segment_duration_seconds=15)
