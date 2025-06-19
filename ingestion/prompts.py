FRAME_EXTRACT_PROMPT = """
        You are a technical expert and presenter.

        You will be given a single image from any source (e.g., slides, manuals, whitepapers, design specs, code, graph etc). For that image:
        1. Generate a **transcript** that explains the image in a clear, concise manner.
        2. Extract the **raw text exactly as it appears in the image**, preserving formatting, labels, and code blocks.
        3. Extract and explain the key technical content (e.g., diagrams, code, architecture, tables, flowcharts).
        4. If there are double quotes in the image, add a backward slash before them for example \"text\".
        5. Be very thorough in your explanations and ensure that the transcript reads naturally as if a presenter is explaining the slide in a talk.
        6. Donot add any additional information than what is present in the image.
        7. Donot add any content that is not utf-8 supported like illegal endline characters, emojis etc..
        8. Donot add any other keys apart from the three keys mentioned in the sample output below.


        Please return the output in the following **valid JSON format**:

      {
        "raw_text": "All visible text extracted from the image, exactly as it appears.",
        "explanation": "A detailed explanation of the contents of the image including diagrams, code, or other elements.",
        "transcript": "A natural-sounding transcript as if a presenter is explaining the slide in a talk."
      }

"""

AUDIO_EXTRACT_PROMPT = """
    System:
    You will be given a single base 64 encoded audio segment.
    
    The segment may be a part of a conversation, meeting, lecture, or may be a standalone conversation. Each segment may also contain **multiple speakers**.
    
    Your tasks are:
    
    1. Understand the context of the audio segment.
    1. Transcribe each audio segment accurately.
    2. Attribute lines to the correct speakers where possible, using labels like "Speaker 1", "Speaker 2", etc.
    3. If speaker identity is not obvious, use "Unknown".
    4. For each segment, structure the transcript as a list of speaker turns.
    5. Do not assume any relationship between segments unless indicated by the content.
    6. Return the result as valid JSON using the structure below.
    7. Donot add any additional information than what is present in the audio segment.
    
    JSON Output Format:
    
    ```json
    {
      "transcript": [
            {
              "speaker": "Speaker 1",
              "text": "Are you ready to learn about this new feature?"
            },
            {
              "speaker": "Speaker 2",
              "text": "Can you please highlight the motive of the meeting first"
            }
          ]
    }

"""

COMBINED_EXTRACT_PROMPT = """
You will receive a JSON object containing multiple segments, each identified by a string key such as "000", "001", etc. Each of these segments 
are small chunks of a larget video of equal length, and they are coherent in chronological order which means 000 is the first segment, 001 is the second, and so on.

Each segment contains:
- `audio_transcript`: A text transcript of the audio. It may involve multiple speakers, labeled as "Speaker 1", "Speaker 2", etc.
- `frame_transcript`: A list of image frame analyses, where each frame includes:
  - `raw_text`: All visible text exactly as it appears in the image
  - `explanation`: A detailed explanation of the technical or visual content
  - `transcript`: A spoken-style explanation of the image as if in a technical talk

Your task is to:
1. Understand each segment's audio and image content and form a coherent narrative.
2. Generate a single, fluent explanation that integrates both the audio and visual information for each segment.
3. Donot add any additional information than what is present in the audio segment or image frames.
4. The combined transcript should be very detailed and thorough.
5. Return your result as a JSON object in the format below:
6. Donot add any non utf-8 characters like emojis, illegal endline characters etc.

```json
{
    'combined_transcript': ' A detailed coherent explanation of the entire video generated after understanding the audio and image content of each segment.'
}

"""

FINAL_PROMPT = """
You will be given one audio segment and multiple images.

Each image and the audio segment are related and should be treated as part of the same scene or explanation.

Your tasks:

1. **Transcribe the audio** segment into a concise, fluent explanation. Summarize it clearly, keeping only the key spoken points. If multiple speakers are present, you may omit speaker labels unless needed for clarity.

2. **For each image**, generate a concise, presentation-style transcript that explains:
   - What is shown
   - Key points in the image
   - Any text or diagrammatic information that’s important

   Return these as a list, one item per image.

3. **Create a single, combined transcript** that integrates both the audio and image content. This should read as if a presenter is explaining the full content in one go — fluent, concise, and logically ordered.

Return your response in the following valid JSON format:

```json
{
  "audio_transcript": "Concise transcription of the audio segment.",
  "image_transcripts": [
    {
      "image_nbr": 1,
      "transcript": "Concise explanation of image 1."
    },
    {
      "image_nbr": 2,
      "transcript": "Concise explanation of image 2."
    }
  ],
  "combined_transcript": "Integrated explanation combining audio and all image content."
}

"""
