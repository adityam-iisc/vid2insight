from enum import Enum

from pydantic import BaseModel


class AgentType(Enum):
    """
    Enum for agent types.
    """
    student_agent = "student_agent"
    doc_agent = "doc_agent"
    chat = "chat"


class Routes(Enum):
    """
    Enum for router types.
    """
    student_subgraph = "student_subgraph"
    doc_subgraph = "doc_subgraph"
    agent_chat = "chat"
    response_format = "response_format"


class AgentResponseModel(BaseModel):
    """
    Model for agent responses.
    """
    chat_content: str
    """
    The content of the chat response.
    """
    doc_content: str | dict
    """
    The content which will be used for writing into a document if applicable. If the response payload is a dictionary of this format {
          "topics": ["Topic 1", "Topic 2", "Topic 3"],
          "questions": [
            {
              "question": "What is the primary function of X?",
              "options": ["Option A", "Option B", "Option C", "Option D"],
              "correct_option": "Option B",
              "topics_covered": ["Topic 1", "Topic 2"]
            },
            ...
          ]
    }, or "topics": ["Topic 1", "Topic 2", "Topic 3"],
      "summary": "A clear and complete explanation of the video content, based entirely on the input context.",
      "study_plan": [
        {
          "day": 1,
          "focus": "Intro to Topic 1",
          "activities": ["Read summary section", "Take notes", "Write a self-explanation"]
        }, 
        ] ... 
        
    Return it as a dictionary with the same structure; else return it as a string.
    """
