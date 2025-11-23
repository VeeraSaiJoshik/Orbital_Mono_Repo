"""
Placeholder tool for testing tool calling functionality.
Returns "3" when called.
"""


def execute() -> str:
    """
    Placeholder tool that returns "3".
    Used for testing tool calling in blockerAgent.
    """
    return "3"


# Tool definition for Anthropic API
TOOL_DEFINITION = {
    "name": "placeholder_tool",
    "description": "A placeholder tool for testing. Call this tool when the user's message contains only numbers.",
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": []
    }
}