from enum import Enum

from pydantic import BaseModel


class AgentType(Enum):
    """
    Enum for agent types.
    """
    student_agent = "student_agent"
    doc_agent = "doc_agent"


class Router(Enum):
    """
    Enum for router types.
    """
    student_subgraph = "student_subgraph"
    doc_subgraph = "doc_subgraph"
    agent_router = "chat"
    response_format = "response_format"


class AgentResponseModel(BaseModel):
    """
    Model for agent responses.
    """
    chat_content: str
    """
    The content of the chat response.
    """
    doc_content: str = ""
    """
    The content which will be used for writing into a document if applicable.
    """
