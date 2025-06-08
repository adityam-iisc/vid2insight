#  VID2Insights (Your Video to Insights Assistant)

![Alt text](To be added)

A GPT/Gemini-based AI application with a Streamlit interface that transforms any video files into standard actionable insights. It also provides a simple chat interface to aid knowledge sharing.

---
## Project Description

### Business Problem
To be updated

---
##  Features

-  **Upload any video `.mp4, .mov ...`**
-  **Choose your desired assistant**
-  **Chat with your video as context** 
-  **Get detailed information considering both audio and video content**
-  **Currently supports following features**:
  - Product Documentation (TXT)
  - Student Notes  (TXT)
  - Visual PPT `To be added in future`
  - To be added 
  - To be added
-  Streamlit interface for a guided experience

---
##  Tech Stack

- `>Python 3.11`
- `Streamlit`
- `OpenCV`
- `LangChain & LangGraph`
- `Azure OpenAI & Gemini AI`
- `Pillow / ImageHash`
- `FPDF`

---
##  Project Structure

```
vid2insight/
├── agent/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── constants.py
│   ├── data/
│   │   └── __init__.py
│   ├── doc_agent/
│   │   └── __init__.py
│   ├── imgs/
│   │   └── __init__.py
│   ├── state/
│   │   └── __init__.py
│   ├── student_agent/
│   │   └── __init__.py
│   ├── ui/
│   │   └── __init__.py
│   ├── utils/
│   │   └── __init__.py
│   └── vid2_insight_graph.py
├── docs/
│   └── __init__.py
├── poetry.lock
├── pyproject.toml
├── README.md
├── Dockerfile
├── templates/
│   └── __init__.py
└── tests/
    └── __init__.py
```

---

##  How to Run

### 1. Clone the Repo
```bash
git clone https://github.com/adityam-iisc/vid2insight.git
cd vid2insiight
```

### 2. Setup virtual env
```bash
python3.13 -m venv venv
source venv/bin/activate
 ```

### 3. Install Dependencies
```bash
pip install poetry
poetry lock
poetry install --no-root
```

### 4. Set Environment Variables
Create a `.env` file:
```
AZURE_OPENAI_API_KEY=your-key (Optional)
AZURE_OPENAI_API_VERSION=your-version (Optional)
GEMINI_API_KEY=your-key
```

### 5. Run the App
```bash
streamlit run app.py
```

