
FRAME_EXTRACT_PROMPT = """
        System:
        You are a technical expert and presenter.

        You will be given one or more images from a technical document (e.g., slides, manuals, whitepapers, design specs). For each image:
        1. Extract the **raw text exactly as it appears in the image**, preserving formatting, labels, and code blocks.
        2. Create transcript of the images.
        3. Extract and explain the key technical content (e.g., diagrams, code, architecture, tables, flowcharts).
        4. Generate a **transcript** that a presenter could speak aloud when presenting the slide or document page.


        Please return the output in the following **valid JSON format**:

        [
          {
            "slide_number": 1,
            "content_of_image": "transcript of the image",
            "raw_text": "All visible text extracted from the image, exactly as it appears.",
            "explanation": "A detailed explanation of the contents of the image including diagrams, code, or other elements.",
            "transcript": "A natural-sounding transcript as if a presenter is explaining the slide in a talk."
          },
          {
            "slide_number": 2,
            "content_of_image": "transcript of the image",
            "raw_text": "Full text from slide 2...",
            "explanation": "Explanation of Slide 2",
            "transcript": "Transcript for Slide 2"
          }
        ]
"""

AUDIO_EXTRACT_PROMPT = """
    System:
    You will be given multiple short audio segments.
    
    Each segment may be a part of a conversation, meeting, lecture, or may be standalone. Each segment may also contain **multiple speakers**.
    
    Your tasks are:
    
    1. Transcribe each audio segment accurately.
    2. Attribute lines to the correct speakers where possible, using labels like "Speaker 1", "Speaker 2", etc.
    3. If speaker identity is not obvious, use "Unknown".
    4. For each segment, structure the transcript as a list of speaker turns.
    5. Do not assume any relationship between segments unless indicated by the content.
    6. Return the result as valid JSON using the structure below.
    
    JSON Output Format:
    
    ```json
    {
      "segments": [
        {
          "segment_id": 1,
          "transcript": [
            {
              "speaker": "Speaker 1",
              "text": "Hello, can you hear me?"
            },
            {
              "speaker": "Speaker 2",
              "text": "Yes, I can hear you clearly."
            }
          ]
        },
        {
          "segment_id": 2,
          "transcript": [
            {
              "speaker": "Unknown",
              "text": "This segment has only one speaker, but the speaker is not identifiable."
            }
          ]
        }
      ]
    }

"""

COMBINED_EXTRACT_PROMPT = """
You will receive a JSON object containing multiple segments, each identified by a string key such as "000", "001", etc.

Each segment contains:
- `audio_transcript`: A text transcript of the audio. It may involve multiple speakers, labeled as "Speaker 1", "Speaker 2", etc.
- `frame_transcript`: A list of image frame analyses, where each frame includes:
  - `image_nbr`: Number of the image in the segment
  - `content_of_image`: A brief natural-language description of the image
  - `raw_text`: All visible text exactly as it appears in the image
  - `explanation`: A detailed explanation of the technical or visual content
  - `transcript`: A spoken-style explanation of the image as if in a technical talk

Your task is to:
1. For each segment:
   - Integrate the **audio transcript** and the **frame transcripts** into a unified, presentation-style `combined_transcript`.
   - Reword the conversation (if multiple speakers) into a single coherent narrative. Remove speaker tags unless they're crucial for clarity.
   - Seamlessly weave the visual content (from the frame transcripts) into the combined explanation.
   - Avoid redundancy but preserve all critical technical content.

2. Return your result as a JSON object in the format below:

```json
{
  "000": {
    "audio_transcript": "Original audio transcript for segment 000, including all speaker lines.",
    "frame_transcript": [ 
      {
        "image_nbr": 1,
        "content_of_image": "...",
        "raw_text": "...",
        "explanation": "...",
        "transcript": "..."
      },
      ...
    ],
    "combined_transcript": "Single, fluent explanation that integrates audio and visual information for segment 000."
  },
  "001": {
    "audio_transcript": "...",
    "frame_transcript": [ ... ],
    "combined_transcript": "..."
  }
}

"""