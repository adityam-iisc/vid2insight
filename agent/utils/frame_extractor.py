import os
import cv2
import base64
import io
import imagehash

from scenedetect import SceneManager, open_video
from scenedetect.detectors import ContentDetector
from typing import List
from PIL import Image
from agent.doc_agent.initialize_logger import logger


def is_hash_unique(seen_hashes, new_hash, tolerance=5) -> bool:
    """
    Returns True if the new_hash is sufficiently different from all hashes in seen_hashes.
    """
    for existing in seen_hashes:
        if abs(new_hash - existing) < tolerance:
            return False
    return True


class FrameExtractor:
    def __init__(self, video_path: str, frame_interval: int = 25, persist: bool = False,
                 segment_duration_seconds: int = 15, max_frames_per_segment: int = 10,
                 scene_detection_threshold: float = 27.0):
        """
        Initializes the FrameExtractor.
        """
        self.video_path = video_path
        self.frame_interval = frame_interval
        self.persist = persist
        self.segment_duration_seconds = segment_duration_seconds
        self.max_frames_per_segment = max_frames_per_segment
        self.scene_detection_threshold = scene_detection_threshold
        if self.persist:
            self.frame_path = os.getenv("FRAME_PATH", "../../docs/frames")
            if not os.path.exists(self.frame_path):
                os.makedirs(self.frame_path)
            else:
                for filename in os.listdir(self.frame_path):
                    file_path = os.path.join(self.frame_path, filename)
                    if os.path.isfile(file_path):
                        if filename.endswith(".keep"):
                            logger.debug(f"Keeping file {filename} in the frame directory.")
                        else:
                            logger.debug(f"Removing file {filename} from the frame directory.")
                            os.remove(file_path)

    def extractor(self, mode: int = 1) -> tuple[List, List]:
        """
        Extract frames using mode:
            1 - every nth frame,
            2 - unique frames with segmentation.
        """
        try:
            if self.persist:
                if not os.path.exists("frames"):
                    logger.debug("Creating directory \\`frames\\` to store extracted frames.")
                else:
                    logger.debug("Directory \\`frames\\` already exists. Frames will be stored here.")
            video = cv2.VideoCapture(self.video_path)
            if not video.isOpened():
                raise FileNotFoundError(f"Could not open video file: {self.video_path}")

            if mode == 1:
                logger.debug("Extracting every nth frame from the video.")
                return self.extraction_of_nth_frame(video)
            elif mode == 2:
                logger.debug("Extracting unique frames from the video using segmentation.")
                return self.get_segmented_frames(video)
            return [], []

        except Exception as e:
            logger.error(f"Error during frame extraction: {e}")
            raise

    def extraction_of_nth_frame(self, video: cv2.VideoCapture) -> tuple[List, List]:
        """
        Extracts every nth frame from the video.
        """
        logger.debug("Extracting every nth frame from the video.")
        frame_index, seen_hashes, base64Frames, frame_paths = 0, set(), [], []
        try:
            while video.isOpened():
                ret, frame = video.read()
                if not ret:
                    break
                if frame_index % self.frame_interval == 0:
                    _, buffer = cv2.imencode(".jpg", frame)
                    pil_img = Image.open(io.BytesIO(buffer.tobytes()))
                    frame_hash = imagehash.phash(pil_img)
                    similar_found = any(abs(frame_hash - existing_hash) < 5 for existing_hash in seen_hashes)
                    if similar_found:
                        frame_index += 1
                        continue
                    seen_hashes.add(frame_hash)
                    if self.persist:
                        logger.debug(f"Saving frame {frame_index} to disk.")
                        frame_file = os.path.join(self.frame_path, f"frame_{frame_index}.jpg")
                        pil_img.save(frame_file)
                        frame_paths.append(frame_file)
                    base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
                frame_index += 1
            video.release()
            if self.persist:
                return base64Frames, frame_paths
            return base64Frames, []
        except Exception as e:
            logger.error(f"Error during nth frame extraction: {e}")
            raise

    def extract_frame_and_hash(self, frame_number: int) -> tuple[str, imagehash.ImageHash] | tuple[None, None]:
        """
        Extracts a specific frame and returns its base64 encoded JPEG and perceptual hash.
        """
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            logger.debug(f"Error: Could not open video file {self.video_path}")
            return None, None
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        cap.release()
        if ret:
            success, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not success:
                return None, None
            pil_img = Image.open(io.BytesIO(buffer.tobytes()))
            hash_val = imagehash.phash(pil_img)
            base64_encoded = base64.b64encode(buffer).decode('utf-8')
            return base64_encoded, hash_val
        return None, None

    def get_segmented_frames(self, video: cv2.VideoCapture) -> tuple[List, List]:
        """
        Processes the video in fixed-duration segments, performs scene detection,
        and extracts representative frames ensuring unique frames even across sampling strategies.
        """
        frame_paths = []
        fps = video.get(cv2.CAP_PROP_FPS)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        video.release()

        segment_frame_length = int(fps * self.segment_duration_seconds)
        total_segments = (total_frames + segment_frame_length - 1) // segment_frame_length

        logger.debug(f"\n--- Video Segmentation Details ---")
        logger.debug(f"Video FPS: {fps:.2f}, Total Frames: {total_frames}")
        logger.debug(f"Segment Duration: {self.segment_duration_seconds} seconds (~{segment_frame_length} frames)")
        logger.debug(f"Total Number of Segments Expected: {total_segments}")
        logger.debug(f"Max Frames per Segment for LLM: {self.max_frames_per_segment}")
        logger.debug(f"Scene Detection Threshold: {self.scene_detection_threshold}")
        logger.debug(f"----------------------------------")

        processed_segments_data = []

        # Global scene detection
        all_scene_frames = []
        try:
            scene_manager = SceneManager()
            scene_manager.add_detector(ContentDetector(threshold=self.scene_detection_threshold))
            logger.debug("\nPerforming global scene detection...")
            video_stream = open_video(self.video_path)
            scene_manager.detect_scenes(video=video_stream)
            all_scenes = scene_manager.get_scene_list(start_in_scene=True)
            logger.debug(f"Global scene detection completed. Total scenes detected: {len(all_scenes)}")
            all_scene_frames = [(s[0].get_frames(), s[1].get_frames()) for s in all_scenes]
        except Exception as e:
            logger.error(
                f"Warning: Error during global scene detection. Falling back to uniform sampling for all segments: {e}")
            all_scene_frames = []

        seen_hashes = set()
        for segment_idx, start_frame_idx in enumerate(range(0, total_frames, segment_frame_length)):
            end_frame_idx = min(start_frame_idx + segment_frame_length - 1, total_frames - 1)
            logger.debug(
                f"\n--- Processing Segment {segment_idx + 1}/{total_segments} (Frames {start_frame_idx} to {end_frame_idx}) ---")

            selected_frames = []

            # Scene candidate selection
            if all_scene_frames:
                candidate_scene_frames = sorted(list(set([
                    f[0] for f in all_scene_frames if start_frame_idx <= f[0] <= end_frame_idx
                ])))
                logger.debug(f"  Scene change frames candidates in this segment: {candidate_scene_frames}")
                for frame_num in candidate_scene_frames:
                    frame_base64, frame_hash = self.extract_frame_and_hash(frame_num)
                    if frame_base64 and frame_hash and is_hash_unique(seen_hashes, frame_hash):
                        seen_hashes.add(frame_hash)
                        selected_frames.append((frame_num, frame_base64))
                        logger.debug(f"  Selected frame {frame_num} using scene candidate.")
                        if len(selected_frames) >= self.max_frames_per_segment:
                            break

            # Uniform sampling if sufficient unique frames not found
            if len(selected_frames) < self.max_frames_per_segment:
                remaining_slots = self.max_frames_per_segment - len(selected_frames)
                temp_uniform_frames = []
                if end_frame_idx == start_frame_idx:
                    temp_uniform_frames.append(start_frame_idx)
                else:
                    step = max(1, (end_frame_idx - start_frame_idx + 1) // (remaining_slots + 1))
                    for i in range(remaining_slots):
                        frame_num = start_frame_idx + (i + 1) * step
                        if frame_num <= end_frame_idx:
                            temp_uniform_frames.append(frame_num)
                    if end_frame_idx not in temp_uniform_frames and end_frame_idx >= start_frame_idx:
                        temp_uniform_frames.append(end_frame_idx)

                for frame_num in sorted(set(temp_uniform_frames)):
                    frame_base64, frame_hash = self.extract_frame_and_hash(frame_num)
                    if frame_base64 and frame_hash and is_hash_unique(seen_hashes, frame_hash):
                        seen_hashes.add(frame_hash)
                        selected_frames.append((frame_num, frame_base64))
                        logger.debug(f"  Selected frame {frame_num} from uniform sampling.")
                        if len(selected_frames) >= self.max_frames_per_segment:
                            break

                if not selected_frames and end_frame_idx >= start_frame_idx:
                    frame_base64, frame_hash = self.extract_frame_and_hash(start_frame_idx)
                    if frame_base64 and frame_hash:
                        seen_hashes.add(frame_hash)
                        selected_frames.append((start_frame_idx, frame_base64))
                    else:
                        logger.debug("  Segment start frame not available.")

            logger.debug(
                f"  **Final unique frames for Segment {segment_idx + 1}: {sorted([frame_num for (frame_num, _) in selected_frames])}**")
            for frame_num, frame_base64 in selected_frames:
                processed_segments_data.append(frame_base64)
                if self.persist:
                    frame_file = os.path.join(self.frame_path, f"segment_{segment_idx}_frame_{frame_num}.jpg")
                    with open(frame_file, "wb") as f:
                        f.write(base64.b64decode(frame_base64))
                    frame_paths.append(frame_file)

        return processed_segments_data, frame_paths


# if __name__ == "__main__":
#     DUMMY_VIDEO_PATH = "C:\\Users\\rushik\\Documents\\tests\\video1.mp4"
#     SEGMENT_DURATION_SECONDS = 15
#     MAX_FRAMES_PER_SEGMENT_FOR_LLM = 10
#     SCENE_DETECTION_THRESHOLD = 27.0
#     extractor = FrameExtractor(video_path=DUMMY_VIDEO_PATH, persist=True,
#                                segment_duration_seconds=SEGMENT_DURATION_SECONDS,
#                                max_frames_per_segment=MAX_FRAMES_PER_SEGMENT_FOR_LLM,
#                                scene_detection_threshold=SCENE_DETECTION_THRESHOLD)
#     segments_data = extractor.extractor(mode=2)