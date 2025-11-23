import os
from typing import Literal
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

CLASSIFIER_PROMPT = """You are an intent classifier. Classify the user's message into one of three categories:

- "blocker" - User is describing a problem, issue, being stuck, blocked, or needs help resolving something
- "update" - User is giving a status update, describing completed work, progress, or what they've done
- "unclear" - Cannot determine intent, greeting, or off-topic

Respond with ONLY one word: blocker, update, or unclear

Examples:
- "I'm stuck on the auth module" → blocker
- "I finished the user profile feature" → update
- "Hey there" → unclear
- "Can't figure out why tests are failing" → blocker
- "Pushed the PR for the dashboard" → update
- "I completed the API integration yesterday" → update
- "There's a bug blocking my progress" → blocker"""


def classify(message: str) -> Literal["blocker", "update", "unclear"]:
    """
    Classify user message intent using Haiku.

    Args:
        message: User's input message

    Returns:
        One of: "blocker", "update", "unclear"
    """
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=10,
        system=CLASSIFIER_PROMPT,
        messages=[{"role": "user", "content": message}]
    )

    result = response.content[0].text.strip().lower()

    # Normalize response
    if "blocker" in result:
        return "blocker"
    elif "update" in result:
        return "update"
    else:
        return "unclear"
