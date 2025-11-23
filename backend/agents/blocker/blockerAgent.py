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

SYSTEM_PROMPT = """You are a helpful AI assistant specialized in resolving blockers for software developers.

You have access to company context including project data, team information, tickets, and past blockers.

Your goal is to:
1. Understand what is blocking the user
2. Search for relevant context and past solutions
3. Connect them with the right people if needed
4. Provide actionable solutions

You have access to tools:
- Use placeholder_tool when the user's message contains only numbers (for testing)
- Use switch_to_update_agent when the user wants to discuss completed work instead of blockers

Be concise and helpful."""

# Available tools
TOOLS = [PLACEHOLDER_TOOL, SWITCH_TOOL]


def get_relevant_context(message: str, top_k: int = 5) -> str:
    """Query Supermemory for relevant context."""
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
        print(f"[BlockerAgent] Error retrieving context: {e}")
        return "Unable to retrieve context from memory."


def handle_tool_call(tool_name: str, tool_input: dict) -> str:
    """Execute the appropriate tool and return result."""
    if tool_name == "placeholder_tool":
        return placeholder_execute()
    else:
        return f"Unknown tool: {tool_name}"


def run(conversation_history: list) -> tuple[str, Optional[str]]:
    """
    Blocker resolution agent with supermem context injection and tool calling.

    Args:
        conversation_history: List of {"role": "user/assistant", "content": "..."} dicts

    Returns:
        Tuple of (response_text, switch_signal)
    """
    # Get the latest user message
    latest_message = conversation_history[-1]["content"] if conversation_history else ""

    # Get supermem context (Option B: inject only for LLM, not into history)
    context = get_relevant_context(latest_message)

    # Build messages for LLM call - copy history and inject context into last message
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

    # Call Claude with tools
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=llm_messages,
        tools=TOOLS
    )

    switch_signal = None

    # Handle tool use if needed
    if response.stop_reason == "tool_use":
        tool_use_block = None
        text_content = ""

        for block in response.content:
            if block.type == "tool_use":
                tool_use_block = block
            elif block.type == "text":
                text_content = block.text

        if tool_use_block:
            print(f"[BlockerAgent] Tool called: {tool_use_block.name}")

            # Check if it's a switch tool - return early with switch signal
            if tool_use_block.name == "switch_to_update_agent":
                print(f"[BlockerAgent] Switch requested → {SWITCH_TARGET}")
                response_text = text_content or "Let me help you with your update."
                return (response_text, SWITCH_TARGET)

            # Execute normal tool
            tool_result = handle_tool_call(tool_use_block.name, tool_use_block.input)
            print(f"[BlockerAgent] Tool result: {tool_result}")

            # Send tool result back to Claude
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
        # No tool use, just get the text response
        response_text = response.content[0].text

    return (response_text, switch_signal)