import uuid

from contracts.agent import AgentResponse
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI

from agent_api.settings import settings
from agent_api.tools.calculator_tool import calculate

# ---------------------------------------------------------------------------
# LLM — ChatOpenAI with API key and timeout from settings.
# temperature=0 means deterministic output — important for a calculator.
# ---------------------------------------------------------------------------

_llm = ChatOpenAI(
    model=settings.llm_model_name,
    api_key=settings.llm_api_key,  # type: ignore[arg-type]
    timeout=settings.llm_timeout_seconds,
    temperature=0,
)

# ---------------------------------------------------------------------------
# Agent — LangChain 1.x create_agent wraps LangGraph under the hood.
# It binds the LLM, tools, and system prompt together.
# The @tool decorator on calculate() already defined the JSON schema
# that the LLM uses to decide how and when to call the tool.
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a calculator assistant for an enterprise platform.

STRICT RULES:
1. You MUST use the calculate tool to answer every arithmetic question.
   Never calculate mentally. Never guess. Always call the tool.
2. Use the exact numbers the user provides — do not round or approximate.
3. If the tool returns an ERROR, report it clearly. Do not make up an answer.
4. Only answer calculator questions. Politely decline anything else.
"""

_agent = create_agent(
    _llm,
    tools=[calculate],
    system_prompt=SYSTEM_PROMPT,
)


async def run(message: str, correlation_id: str = "") -> AgentResponse:
    """
    Run the Calculator Agent for a single user message.

    LangChain 1.x handles the tool-calling loop automatically:
    1. LLM receives message + tool definitions
    2. LLM decides to call calculate tool
    3. LangChain executes the tool
    4. Result goes back to LLM
    5. LLM forms the final answer

    Response is a list of messages — we read the last one for the answer.
    """
    if not correlation_id:
        correlation_id = str(uuid.uuid4())

    result = await _agent.ainvoke({"messages": [HumanMessage(content=message)]})

    messages = result.get("messages", [])

    # Final answer is always the last message from the LLM.
    answer = messages[-1].content if messages else "No answer returned."

    # Check if any tool was actually called during execution.
    # ToolMessage appears in the message list when a tool was invoked.
    tool_called = any(isinstance(m, ToolMessage) for m in messages)

    return AgentResponse(
        answer=answer,
        tool_called=tool_called,
        correlation_id=correlation_id,
    )
