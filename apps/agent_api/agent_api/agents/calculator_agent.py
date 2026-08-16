import json
import uuid
from decimal import Decimal
from typing import Any, cast

from contracts.agent import AgentResponse
from openai import AsyncOpenAI

from agent_api.settings import settings
from agent_api.tools.calculator_tool import calculate

# ---------------------------------------------------------------------------
# OpenAI client — shared instance for the agent.
# ---------------------------------------------------------------------------

_client = AsyncOpenAI(
    api_key=settings.llm_api_key,
    timeout=settings.llm_timeout_seconds,
)

# ---------------------------------------------------------------------------
# Tool definition — describes the calculate tool to OpenAI.
#
# OpenAI reads this and knows:
#   - what the tool is called
#   - what parameters it accepts
#   - what each parameter means
#
# The LLM uses this to decide when and how to call the tool.
# ---------------------------------------------------------------------------

CALCULATE_TOOL = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": (
            "Performs arithmetic calculations. "
            "ALWAYS use this tool to answer maths questions — "
            "never calculate mentally or guess the answer."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The arithmetic operation to perform",
                },
                "a": {
                    "type": "number",
                    "description": "First operand",
                },
                "b": {
                    "type": "number",
                    "description": "Second operand",
                },
            },
            "required": ["operation", "a", "b"],
        },
    },
}

# ---------------------------------------------------------------------------
# System prompt — defines the agent's behaviour.
#
# Key rules enforced here:
#   1. Must use the calculate tool — never answer arithmetic directly.
#   2. Must preserve exact operation and operands — no rounding or guessing.
#   3. If the tool fails, report the failure honestly — no hallucinated answer.
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a calculator assistant for an enterprise platform.

STRICT RULES:
1. You MUST use the calculate tool to answer every arithmetic question.
   Never calculate mentally. Never guess. Always call the tool.
2. Use the exact numbers the user provides — do not round or approximate.
3. If the tool returns an error, report it clearly. Do not make up an answer.
4. Only answer calculator questions. Politely decline anything else.
"""


async def run(message: str, correlation_id: str = "") -> AgentResponse:
    """
    Run the Calculator Agent for a single user message.

    Flow:
    1. Send user message + tool definition to OpenAI
    2. OpenAI decides to call the calculate tool
    3. We execute the actual HTTP call to the calculator service
    4. Send the result back to OpenAI
    5. OpenAI forms the final answer
    6. Return AgentResponse

    The agent never does arithmetic — it only orchestrates tool calls.
    """

    if not correlation_id:
        correlation_id = str(uuid.uuid4())

    # Use Any for messages list — OpenAI SDK types are strict but we build
    # the list dynamically by appending tool results alongside typed messages.
    messages: list[Any] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message},
    ]

    # Step 1 — ask OpenAI what to do, give it the calculate tool.
    # type: ignore needed because OpenAI SDK Pyright types are stricter than
    # what the API actually accepts at runtime for plain dicts.
    response = await _client.chat.completions.create(
        model=settings.llm_model_name,
        messages=messages,
        tools=cast(Any, [CALCULATE_TOOL]),
        tool_choice="auto",
    )

    choice = response.choices[0]
    tool_called = False

    # Step 2 — did OpenAI decide to call a tool?
    if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
        tool_called = True
        tool_call = choice.message.tool_calls[0]
        # function attribute exists on all standard tool calls at runtime.
        args = json.loads(tool_call.function.arguments)  # type: ignore[union-attr]

        # Step 3 — execute the actual tool call (HTTP call to calculator).
        tool_result = await calculate(
            operation=args["operation"],
            a=Decimal(str(args["a"])),
            b=Decimal(str(args["b"])),
            correlation_id=correlation_id,
        )

        # Step 4 — send the tool result back to OpenAI so it can form the answer.
        messages.append(choice.message)
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,  # type: ignore[union-attr]
                "content": json.dumps(
                    {
                        "success": tool_result.success,
                        "code": tool_result.code,
                        "result": tool_result.data.get("result") if tool_result.success else None,
                        "message": tool_result.message,
                    }
                ),
            }
        )

        # Step 5 — get the final answer from OpenAI.
        final_response = await _client.chat.completions.create(  # type: ignore[call-overload]
            model=settings.llm_model_name,
            messages=messages,
        )
        answer = final_response.choices[0].message.content or "No answer returned."

    else:
        # OpenAI chose not to call a tool — answer directly.
        # This happens for non-maths questions (greetings, out-of-scope).
        answer = choice.message.content or "I can only help with arithmetic calculations."

    return AgentResponse(
        answer=answer,
        tool_called=tool_called,
        correlation_id=correlation_id,
    )
