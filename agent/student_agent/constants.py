from enum import Enum
from typing import List

from pydantic import BaseModel, Field

class Routes(Enum):
    """
    Enumeration of the available routes for the agent.

    Attributes:
        CONTEXT: Represents the context route.
        SUMMARY: Represents the summary route.
        MCQ: Represents the multiple-choice question route.
        EVALUATOR: Represents the evaluator route.
    """
    CONTEXT = "context"
    SUMMARY = "summary"
    MCQ = "mcq"
    CHAT = 'chat'
    EVALUATOR = 'evaluator'
    END = 'end'

    @classmethod
    def get_route(cls, route_name: str):
        """
        Retrieve the route enum value based on the provided route name.

        Args:
            route_name (str): The name of the route to retrieve.

        Returns:
            Routes: The corresponding route enum value.

        Raises:
            ValueError: If the provided route name is not valid.
        """
        try:
            return cls[route_name.upper()]
        except KeyError:
            raise ValueError(f"Invalid route name: '{route_name}'. Available routes are: {', '.join(cls.__members__.keys())}.")


class Intent(Enum):
    """
    Enumeration of the available intents for the agent.

    Attributes:
        GENERATE_EXEC_SUMMARY: Represents the intent to generate an executive summary.
        GENERATE_DOCS: Represents the intent to generate product documents.
        DOC_CHAT: Represents the intent for document chat interactions.
    """
    GENERATE_SUMMARY = "generate_summary"
    GENERATE_MCQ = "generate_mcq"
    DOC_CHAT = "doc_chat"

    @classmethod
    def get_intent(cls, intent_name: str):
        """
        Retrieve the intent enum value based on the provided intent name.

        Args:
            intent_name (str): The name of the intent to retrieve.

        Returns:
            Intent: The corresponding intent enum value.

        Raises:
            ValueError: If the provided intent name is not valid.
        """
        try:
            return cls[intent_name.upper()]
        except KeyError:
            raise ValueError(f"Invalid intent name: '{intent_name}'. Available intents are: {', '.join(cls.__members__.keys())}.")


class EvaluatorResponseModel(BaseModel):
    """
    Model representing the response from the evaluator.
    """
    feedback: str = Field(description="feedback for the user based on the evaluation")
    is_modification_required: bool = Field(description="Indicates whether a modification is required based on the evaluation")


class SummaryResponseModel(BaseModel):
    """
    Model representing the response for a summary request.
    """
    topics: List[str] = Field(default_factory=list, description="List of topics covered in the video")
    summary: str = Field(default="", description="An overall of the video content, highlighting key points and concepts from an educational perspective")
    study_plan: List[dict[str, str]] = Field(default=[], description="A structured study plan for the user, detailing daily focuses and activities to reinforce learning. Each entry should include a 'day', 'focus', and 'activities'.")
    prerequisites: list[str] = Field(default_factory=list, description="List of prerequisites for understanding the content, or empty if none suggested")


class MCQResponseModel(BaseModel):
    """
    Model representing the response for a multiple-choice question (MCQ) request.
    """
    topics: List[str] = Field(default_factory=list[str], description="List of topics covered in the entire video")
    questions: List[dict[str, str]] = Field(default_factory=list[dict[str,str]], description="List of multiple-choice questions generated from the video content. Each question should include the question text, options, correct option, and topics covered for that particular question.")