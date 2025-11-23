def execute() -> str:
    return "4"


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