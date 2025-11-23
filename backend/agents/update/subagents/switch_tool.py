"""
Switch tool for transitioning from update agent to blocker agent.
This is a signal tool - it doesn't execute anything, just triggers routing.
"""

# Tool definition for Anthropic API
TOOL_DEFINITION = {
    "name": "switch_to_blocker_agent",
    "description": "Call this when the user mentions a blocker, issue, problem, or something they're stuck on instead of progress updates. Use this when the conversation shifts from status reporting to problem-solving.",
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

# The target agent to switch to
SWITCH_TARGET = "blocker"