"""
Switch tool for transitioning from blocker agent to update agent.
This is a signal tool - it doesn't execute anything, just triggers routing.
"""

# Tool definition for Anthropic API
TOOL_DEFINITION = {
    "name": "switch_to_update_agent",
    "description": "Call this when the user wants to discuss completed work, progress updates, or task status instead of blockers. Use this when the conversation shifts from problem-solving to status reporting.",
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

# The target agent to switch to
SWITCH_TARGET = "update"