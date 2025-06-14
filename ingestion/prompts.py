FRAME_EXTRACT_PROMPT = """
        System:
        You are a technical expert and presenter.

        You will be given one or more images from a technical document (e.g., slides, manuals, whitepapers, design specs). For each image:

        1. Extract and explain the key technical content (e.g., diagrams, code, architecture, tables, flowcharts).
        2. Generate a **transcript** that a presenter could speak aloud when presenting the slide or document page.

        Use the following output format:

        -----------------------
        Slide {n}

        🔹 Summary:
        - [Brief summary of the key topic, concept, or process shown in the image.]
        - [List 1–3 bullet points of core technical ideas.]

        🔹 Explanation:
        [Detailed breakdown of the slide/page: explain what is shown, how it works, and any relationships between components.]

        🔹 Transcript:
        "Good morning. On this slide, we see [...]. This diagram shows how [...]. Notice that [...]. The key takeaway here is [...]."

        -----------------------

        Assume the audience is technically proficient (e.g., engineers or graduate students), but not familiar with this specific document.

        Please label your response for each image accordingly (e.g., Slide 1, Slide 2, etc.).

"""
FRAME_EXTRACT_PROMPT_2 = """
        System:
        You are a technical expert and presenter.

        You will be given one or more images from a technical document (e.g., slides, manuals, whitepapers, design specs). For each image:
        1. Extract the **raw text exactly as it appears in the image**, preserving formatting, labels, and code blocks.
        2. Create transcript of the images. Summarize the content in each image
        3. Extract and explain the key technical content (e.g., diagrams, code, architecture, tables, flowcharts).
        4. Generate a **transcript** that a presenter could speak aloud when presenting the slide or document page.


        Please return the output in the following **valid JSON format**:

        [
          {
            "slide_number": 1,
            "content_of_image": "transcript of the image",
            "raw_text": "All visible text extracted from the image, exactly as it appears.",
            "summary": {
              "title": "Brief summary of what the image is about.",
              "bullet_points": [
                "Key technical point 1",
                "Key technical point 2",
                "Key technical point 3"
              ]
            },
            "explanation": "A detailed explanation of the contents of the image including diagrams, code, or other elements.",
            "transcript": "A natural-sounding transcript as if a presenter is explaining the slide in a talk."
          },
          {
            "slide_number": 2,
            "content_of_image": "transcript of the image",
            "raw_text": "Full text from slide 2...",
            "summary": {
              "title": "Another slide topic summary",
              "bullet_points": [
                "Point A",
                "Point B"
              ]
            },
            "explanation": "Explanation of Slide 2",
            "transcript": "Transcript for Slide 2"
          }
        ]
"""

AUDIO_EXTRACT_PROMPT_2 = """
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
System:
You will receive multiple groups of multimodal content.

Each group contains:
- One audio segment (which may contain one or more speakers)
- One or more images from a technical document (e.g., slides, manuals, whitepapers, or design specs)

Your task is to process **each group independently** and return structured output for every group in the JSON format below.

For each group:

1. Accurately **transcribe the audio**. If multiple speakers are present, reflect changes in speakers where possible, using labels like "Speaker 1", "Speaker 2", etc. If unclear, use "Unknown".

2. For each image in the group:
    - Extract and return the **visible text** exactly as it appears (`raw_text`)
    - Describe the **content of the image** in natural language
    - Provide a **summary** with:
      - A short `title`
      - A few high-level bullet points (`bullet_points`)
    - Write an **explanation** of diagrams, charts, or technical content in the image
    - Generate a **natural-sounding transcript** as if a presenter is explaining the image to a technical audience

3. Then, generate a **combined transcript** that integrates the audio and the image content — as if a single presenter is delivering both parts cohesively in a live technical presentation.

**Return your response in the following JSON structure** (per group):

```json
[
  {
    "audio_transcript": "Verbatim transcript of the audio segment with speaker attribution if available.",
    "image_transcript": [
      {
        "image_nbr": 1,
        "content_of_image": "Summary of what's shown in the image.",
        "raw_text": "All visible text exactly as it appears in the image.",
        "summary": {
          "title": "One-line summary of the image topic.",
          "bullet_points": [
            "Key technical point 1",
            "Key technical point 2",
            "Key technical point 3"
          ]
        },
        "explanation": "Detailed explanation of diagrams, code, or visual content in the image.",
        "transcript": "Spoken-style transcript explaining the image as if in a talk."
      },
      {
        "image_nbr": 2,
        "content_of_image": "...",
        ...
      }
    ],
    "combined_transcript": "Single, smooth transcript that blends the audio content and image explanations into one cohesive spoken narrative."
  },
  ...
]

"""