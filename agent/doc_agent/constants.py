from enum import Enum

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