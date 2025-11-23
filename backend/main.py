from typing import Literal, Optional
from agents.classifier import classify
from agents.blocker.blockerAgent import run as blocker_run
from agents.update.updateAgent import run as update_run

class SessionOrchestrator:
    def __init__(self):
        self.conversation_history: list[dict] = []
        self.active_agent: Optional[Literal["blocker", "update"]] = None

    def handle_message(self, user_message: str) -> str:
        """
        Args:
            user_message: The user's input

        Returns:
            Agent's response string
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # If no active agent, classify intent
        if self.active_agent is None:
            intent = classify(user_message)
            print(f"[Classifier] Intent: {intent}")

            if intent == "unclear":
                response = "Hey! Are you looking to talk through a blocker, or give an update on what you've been working on?"
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                return response

            self.active_agent = intent
            print(f"[Orchestrator] Routing to: {self.active_agent}")

        # Route to active agent
        if self.active_agent == "blocker":
            response, switch_signal = blocker_run(self.conversation_history)
        else:
            response, switch_signal = update_run(self.conversation_history)

        # Add response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })

        # Handle agent switching
        if switch_signal:
            print(f"[Orchestrator] Switching to: {switch_signal}")
            self.active_agent = switch_signal

        return response

    def reset(self):
        """Reset conversation state."""
        self.conversation_history = []
        self.active_agent = None


def interactive_chat():
    """Run an interactive chat session for testing."""
    print("=" * 60)
    print("STANDUP AI - Orchestrator Test")
    print("=" * 60)
    print("Test the routing: try blocker messages (get '1') or update messages (get '2')")
    print("Type 'quit' to exit, 'reset' to start over\n")

    orchestrator = SessionOrchestrator()

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break

        if user_input.lower() == 'reset':
            orchestrator.reset()
            print("[System] Conversation reset")
            continue

        if not user_input:
            continue
        response = orchestrator.handle_message(user_input)
        print(f"\nAssistant: {response}")
        print(f"[Active Agent: {orchestrator.active_agent}]")


if __name__ == "__main__":
    interactive_chat()
