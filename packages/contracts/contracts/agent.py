from uuid import UUID

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """
    What the user sends to POST /api/v1/agent/query.

    Just a natural language message — the agent figures out the rest.
    conversation_id lets the agent maintain context across multiple messages
    in the same conversation (used in later iterations).
    """

    message: str = Field(description="Natural language question or request")

    # Optional — links this request to an ongoing conversation.
    # None means this is a standalone request.
    conversation_id: UUID | None = Field(default=None)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"message": "What is 25 multiplied by 8?"},
                {"message": "What is 100 divided by 4?"},
            ]
        }
    }


class AgentResponse(BaseModel):
    """
    What the agent returns to the user.

    answer       — the human-readable result
    tool_called  — True if the agent actually called a tool (it must — no mental arithmetic)
    correlation_id — ties this response to the trace for observability
    """

    answer: str = Field(description="Human-readable answer from the agent")

    # Confirms the agent used the calculate tool, not mental arithmetic.
    # In tests we assert this is always True for calculation questions.
    tool_called: bool = Field(description="Whether a tool was invoked to produce the answer")

    # Ties this response back to the request for distributed tracing.
    correlation_id: str = Field(default="")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "answer": "25 multiplied by 8 is 200.",
                    "tool_called": True,
                    "correlation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                }
            ]
        }
    }
