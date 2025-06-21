from enum import Enum
from pydantic import BaseModel, Field


class Routes(Enum):
    """
    Enumeration of the available routes for the agent.

    Attributes:
        CONTEXT: Represents the route for context-related operations.
        PRODUCT_DOCUMENTS: Represents the route for handling product documents.
        EXECUTIVE_SUMMARY: Represents the route for generating executive summaries.
        DOC_CHAT`: Represents the route for document chat interactions.
    """
    CONTEXT = "context"
    PRODUCT_DOCUMENTS = "product_documents"
    EXECUTIVE_SUMMARY = "executive_summary"
    DOC_CHAT = "doc_chat"
    EVALUATOR = "evaluator"

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
            raise ValueError(
                f"Invalid route name: '{route_name}'. Available routes are: {', '.join(cls.__members__.keys())}.")


class Intent(Enum):
    """
    Enumeration of the available intents for the agent.

    Attributes:
        GENERATE_EXEC_SUMMARY: Represents the intent to generate an executive summary.
        GENERATE_DOCS: Represents the intent to generate product documents.
        DOC_CHAT: Represents the intent for document chat interactions.
    """
    GENERATE_EXEC_SUMMARY = "generate_exec_summary"
    GENERATE_DOCS = "generate_docs"
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
            raise ValueError(
                f"Invalid intent name: '{intent_name}'. Available intents are: {', '.join(cls.__members__.keys())}.")



from pydantic import BaseModel, Field

class EvaluatorResponseModel(BaseModel):
    """
    Model representing the response from the evaluator.
    """
    feedback: str = Field(description="feedback for the user based on the evaluation")
    is_modification_required: bool = Field(description="Indicates whether a modification is required based on the evaluation")