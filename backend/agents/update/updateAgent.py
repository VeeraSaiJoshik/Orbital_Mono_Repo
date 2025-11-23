import os
from typing import Optional
from anthropic import Anthropic
from supermemory import Supermemory
from dotenv import load_dotenv

from .subagents.placeholder_tool import execute as placeholder_execute, TOOL_DEFINITION as PLACEHOLDER_TOOL
from .subagents.switch_tool import TOOL_DEFINITION as SWITCH_TOOL, SWITCH_TARGET

load_dotenv()

# Initialize clients
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
supermemory_client = Supermemory(api_key=os.getenv("SUPERMEMORY_API_KEY"))

SYSTEM_PROMPT = """You are a helpful AI assistant specialized in tracking work updates for software developers.

You have access to company context including project data, team information, tickets, and past work.

Your goal is to:
1. Understand what work the user has completed
2. Verify their updates against available context
3. Help them update project management tools (Jira, Asana, etc.)
4. Generate clear summaries of their progress

You have access to tools:
- Use placeholder_tool when the user's message contains only numbers (for testing)
- Use switch_to_blocker_agent when the user mentions a blocker or problem instead of updates

Be concise and helpful."""

# Available tools
TOOLS = [PLACEHOLDER_TOOL, SWITCH_TOOL]


def get_relevant_context(message: str, top_k: int = 5) -> str:
    try:
        results = supermemory_client.search.execute(q=message)

        if not results.results or len(results.results) == 0:
            return "No relevant context found in memory."

        context = "=== RELEVANT COMPANY CONTEXT ===\n\n"
        for idx, memory in enumerate(results.results[:top_k], 1):
            memory_content = memory.chunks[0].content if memory.chunks else memory.title
            context += f"[Memory {idx}]\n{memory_content}\n\n"

        return context
    except Exception as e:
        print(f"[UpdateAgent] Error retrieving context: {e}")
        return "Unable to retrieve context from memory."


def handle_tool_call(tool_name: str, tool_input: dict) -> str:
    """Execute the appropriate tool and return result."""
    if tool_name == "placeholder_tool":
        return placeholder_execute()
    else:
        return f"Unknown tool: {tool_name}"


def run(conversation_history: list) -> tuple[str, Optional[str]]:

    latest_message = conversation_history[-1]["content"] if conversation_history else ""
    context = get_relevant_context(latest_message)

    llm_messages = []
    for i, msg in enumerate(conversation_history):
        if i == len(conversation_history) - 1 and msg["role"] == "user":
            # Inject context into the latest user message only
            llm_messages.append({
                "role": "user",
                "content": f"{context}\n\n=== USER MESSAGE ===\n{msg['content']}"
            })
        else:
            llm_messages.append(msg.copy())

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=llm_messages,
        tools=TOOLS
    )

    switch_signal = None

    if response.stop_reason == "tool_use":
        tool_use_block = None
        text_content = ""

        for block in response.content:
            if block.type == "tool_use":
                tool_use_block = block
            elif block.type == "text":
                text_content = block.text

        if tool_use_block:
            print(f"[UpdateAgent] Tool called: {tool_use_block.name}")

            # Check if it's a switch tool - return early with switch signal
            if tool_use_block.name == "switch_to_blocker_agent":
                print(f"[UpdateAgent] Switch requested → {SWITCH_TARGET}")
                response_text = text_content or "Let me help you with that blocker."
                return (response_text, SWITCH_TARGET)

            # Execute normal tool
            tool_result = handle_tool_call(tool_use_block.name, tool_use_block.input)
            print(f"[UpdateAgent] Tool result: {tool_result}")

            llm_messages.append({
                "role": "assistant",
                "content": response.content
            })
            llm_messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use_block.id,
                    "content": tool_result
                }]
            })

            # Get final response
            final_response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                system=SYSTEM_PROMPT,
                messages=llm_messages,
                tools=TOOLS
            )

            response_text = final_response.content[0].text
    else:
        response_text = response.content[0].text

    return (response_text, switch_signal)
