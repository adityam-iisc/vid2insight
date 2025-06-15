import io
import math
import os
import subprocess
import logging
import shutil

from pydub import AudioSegment
from agent.config.initialize_logger import logger


class VideoAudioProcessor:
    """
    Processor to extract the primary audio track from a video file (and or persist/chunk it).
    """
    def __init__(self, input_path: str, output_path: str, interval_s: int = -1, ffmpeg_path: str = "ffmpeg", persist: bool = False):
        """
        Initializes the VideoAudioProcessor with the given parameters.
        :param input_path: Input video file path, must end with the filename
        :param output_path: Output audio file path, must end with the filename and extension (e.g., abc.wav)
        :param interval_s: If you wish to retrieve the audio in chunks, specify the interval in seconds. (default: -1)
        :param ffmpeg_path: Specify the path to the ffmpeg executable. (default: "ffmpeg")
        :param persist: If you wish to persist the audio in your disk, set this to True. (default: False)
        """
        self.ffmpeg_path = ffmpeg_path
        self.input_path = input_path
        self.output_path = output_path
        self.interval_s = interval_s
        self.sample_rate = 16000
        self.channels = 1  # Mono audio, ultimately converted to by Gemini
        self.persist = persist
        if shutil.which(self.ffmpeg_path) is None:
            raise EnvironmentError(f"ffmpeg not found at path '{self.ffmpeg_path}'. Please install ffmpeg\nIf using macos use brew install ffmpeg.\nFor other platforms, please clone the repo")
        self.logger = logging.getLogger(self.__class__.__name__)
    def _run_ffmpeg_command(self, cmd: list) -> None:
        """
        Runs the given ffmpeg command using subprocess.
        :param cmd: List of command arguments to be passed to ffmpeg.
        :raises RuntimeError: If the ffmpeg command fails.
        """
        try:
            self.logger.debug(f"Running ffmpeg command: {' '.join(cmd)}")
            completed = subprocess.run(cmd, capture_output=True, text=True)
            if completed.returncode != 0:
                err = completed.stderr.strip()
                raise RuntimeError(f"ffmpeg failed: {err}")
            self.logger.info("ffmpeg command executed successfully.")
        except Exception as e:
            self.logger.error(f"ffmpeg command execution failed: {e}")
            raise
    def _extract_audio(self) -> str:
        """
        Extracts the audio from the given video file and writes it to output_audio_path.
        Converts audio to the specified sample rate and channels (mono by default).
        Returns the path to the output audio file.

        Raises:
            FileNotFoundError: if the video file does not exist.
            RuntimeError: if ffmpeg fails to extract or convert audio.
        """
        if self.interval_s != -1 and self.persist:
            base, ext = os.path.splitext(self.output_path)
            cmd1 = [
                self.ffmpeg_path,
                "-i", self.input_path,
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", str(self.sample_rate),
                "-ac", str(self.channels),
                "-y",  # overwrite without asking
                self.output_path
            ]
            self._run_ffmpeg_command(cmd1)
            cmd2 = [
                self.ffmpeg_path,
                "-i", self.output_path,
                "-f", "segment",
                "-segment_time", str(self.interval_s),
                "-ar", str(self.sample_rate),
                "-ac", str(self.channels),
                "-c", "copy",
                f"{base}_%03d{ext}"
            ]
            self._run_ffmpeg_command(cmd2)

        else:
            cmd = [
                self.ffmpeg_path,
                "-i", self.input_path,
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", str(self.sample_rate),
                "-ac", str(self.channels),
                "-y",  # overwrite without asking
                self.output_path
            ]
        return self.output_path
        # try:
        #     final_cmd = ' '.join(cmd)
        #     self.logger.debug(f"Running ffmpeg command: {' '.join(cmd)}")
        #     completed = subprocess.run(cmd, capture_output=True, text=True)
        #     if completed.returncode != 0:
        #         err = completed.stderr.strip()
        #         raise RuntimeError(f"ffmpeg failed: {err}")
        #     self.logger.info(f"Extracted audio to '{self.output_path}'.")
        #     return self.output_path
        # except Exception as e:
        #     self.logger.error(f"Audio extraction failed: {e}")
        #     raise

    def _audio_to_bytestream(self) -> list:
        """
        Splits the audio file into chunks of specified duration.
        :returns a list of paths to the chunked audio files.
        :raises any Exception: If there is an error during audio extraction or conversion.
        """
        try:
            op_path = self._extract_audio()
            audio = AudioSegment.from_file(op_path, format="wav")

            print("Output path", self.output_path)
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            if os.path.exists(self.output_path):

                os.remove(self.output_path)
            if self.interval_s:
                if self.persist:
                    # If persist is True, we will create multiple files
                    logger.info(f"Persisting audio chunks of {self.interval_s} seconds each, bytestream wont be generated for this")
                    return []
                chunk_length_ms = self.interval_s * 1000  # Convert seconds to milliseconds
                num_chunks = math.ceil(len(audio) / chunk_length_ms)

                # Create a list to hold the chunks
                chunks = [audio[i * chunk_length_ms: (i + 1) * chunk_length_ms] for i in range(num_chunks)]
                chunk_bytes_list = []
                for chunk in chunks:
                    chunk_io = io.BytesIO()
                    chunk.export(chunk_io, format="wav")
                    chunk_io.seek(0)
                    chunk_bytes_list.append(chunk_io)
            else:
                chunk_bytes_list = [audio.export(format="wav")]

            return chunk_bytes_list
        except Exception as e:
            self.logger.error(f"Error extracting audio: {e}")
            raise

    def extractor(self) -> list:
        """
        Primary method to extract or persist audio from the video file as bytestream or wav files onto the disk.
        :return: A list of audio chunks as byte streams.
        :raises any Exception: If there is an error during audio extraction or conversion.
        """
        try:
            if not os.path.isfile(self.input_path):
                raise FileNotFoundError(f"Video file '{self.input_path}' does not exist.")
            # Ensure output directory exists
            os.makedirs(os.path.dirname(self.output_path) or ".", exist_ok=True)

            return self._audio_to_bytestream()
        except Exception as e:
            self.logger.error(f"Error extracting audio: {e}")
            raise

#
# Example usage:
# ===============================================
# mono - convert video to audio in a single file
# ===============================================
# if __name__ == "__main__":
#     aob = VideoAudioProcessor(
#         # input_path='../../docs/abc.mp4',
#         # output_path='../../docs/audio_output.wav',
#         input_path="C:\\Users\\rushik\\Documents\\tests\\video1.mp4",
#         output_path="C:\\Users\\rushik\\Documents\\tests\\audio_output.wav",
#         interval_s=-1,
#         persist=True
#     )
#     chunks = aob.extractor()
#     print(chunks)
    # audio_transcript(chunks)

# ===============================================
# convert video to audio and persist it in segments of duration interval_s
# ===============================================
# if __name__ == "__main__":
#     video_id = "1234"
#     aob = VideoAudioProcessor(
#         # input_path='../../docs/abc.mp4',
#         # output_path='../../docs/audio_output.wav',
#         # ==== valid ====
#         # input_path="C:\\Users\\rushik\\Documents\\tests\\video1.mp4",
#         # output_path="C:\\Users\\rushik\\Documents\\tests\\audio_output.wav",
#         input_path="C:\\Users\\rushik\\Documents\\tests\\video1.mp4",
#         output_path=f"../docs/{video_id}/audio_segments/audio_output.wav",
#         interval_s=15,
#         persist=True
#     )
#     chunks = aob.extractor()
    # print(chunks)
    # audio_transcript(chunks)
