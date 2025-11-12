import os
from anthropic import Anthropic
from supermemory import Supermemory
from dotenv import load_dotenv

load_dotenv()

# Initialize clients
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
supermemory_client = Supermemory(api_key=os.getenv("SUPERMEMORY_API_KEY"))


def get_relevant_context(user_message, top_k=5):
    """
    Query Supermemory for relevant context based on user message

    Args:
        user_message: The user's current message
        top_k: Number of top memories to retrieve

    Returns:
        String of relevant context from Supermemory
    """
    try:
        # Query Supermemory with the user's message
        results = supermemory_client.search.execute(
            q=user_message
        )

        # Debug: Print response structure (can remove after testing)
        print(f"Debug - Search results: {results}")
        if results.results:
            print(f"Debug - First result structure: {results.results[0]}")

        if not results.results or len(results.results) == 0:
            return "No relevant context found in memory."

        # Format the retrieved memories into context
        context = "=== RELEVANT COMPANY CONTEXT ===\n\n"
        for idx, memory in enumerate(results.results[:top_k], 1):
            # Access content from chunks array
            memory_content = memory.chunks[0].content if memory.chunks else memory.title
            context += f"[Memory {idx}]\n{memory_content}\n\n"

        return context

    except Exception as e:
        print(f"Error retrieving context: {e}")
        return "Unable to retrieve context from memory."


def chat_with_project_identifier(user_message, conversation_history):
    """
    Main chat function that identifies projects from conversation
    
    Args:
        user_message: Current user message
        conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
    
    Returns:
        dict with 'response' and 'predicted_project'
    """
    
    # Get relevant context from Supermemory
    context = get_relevant_context(user_message)
    
    # System prompt
    system_prompt = """You are a helpful AI assistant with access to company project data, team information, tickets, and blockers.

Your primary goal is to identify which project the user is discussing based on the conversation context and the relevant company data provided.

For each response, you must:
1. Respond naturally to the user's question or comment
2. Make your best guess about which project is being discussed
3. Format your response as follows:

<response>
[Your natural conversational response here]
</response>

<project_prediction>
Project ID: [proj-XXX or "Unknown"]
Confidence: [High/Medium/Low]
Reasoning: [Brief explanation of why you think it's this project]
</project_prediction>

Use the provided context to make informed predictions. Look for clues like:
- Specific technologies mentioned (React, ML, Flask, etc.)
- Team member names
- Ticket IDs or blocker IDs
- Problem descriptions that match known issues
- Feature descriptions that match project descriptions"""

    # Build the full conversation with context injection
    messages = []
    
    # Add conversation history
    for msg in conversation_history:
        messages.append(msg)
    
    # Add current message with injected context
    current_message = f"{context}\n\n=== USER MESSAGE ===\n{user_message}"
    messages.append({
        "role": "user",
        "content": current_message
    })
    
    # Call Claude
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=system_prompt,
        messages=messages
    )
    
    # Parse the response
    full_response = response.content[0].text
    
    # Extract response and prediction
    try:
        response_part = full_response.split("<response>")[1].split("</response>")[0].strip()
        prediction_part = full_response.split("<project_prediction>")[1].split("</project_prediction>")[0].strip()
    except:
        # Fallback if parsing fails
        response_part = full_response
        prediction_part = "Unable to parse prediction"
    
    return {
        "response": response_part,
        "prediction": prediction_part,
        "full_response": full_response
    }


def interactive_chat():
    """Run an interactive chat session"""
    print("="*60)
    print("PROJECT IDENTIFIER CHATBOT")
    print("="*60)
    print("Chat with me about your work, and I'll try to identify which project you're discussing!")
    print("Type 'quit' to exit\n")
    
    conversation_history = []
    
    while True:
        # Get user input
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        if not user_input:
            continue
        
        # Get response
        print("\n[Thinking...]")
        result = chat_with_project_identifier(user_input, conversation_history)
        
        # Display response
        print(f"\nAssistant: {result['response']}")
        print(f"\n{'─'*60}")
        print(f"📊 PROJECT PREDICTION:")
        print(result['prediction'])
        print(f"{'─'*60}")
        
        # Update conversation history (without the injected context)
        conversation_history.append({
            "role": "user",
            "content": user_input
        })
        conversation_history.append({
            "role": "assistant",
            "content": result['full_response']
        })


# Example of programmatic usage
def example_usage():
    """Example of how to use the chatbot programmatically"""
    
    # Start with empty conversation
    conversation = []
    
    # First message
    msg1 = "I'm having trouble with the sentiment widget showing blank on staging"
    result1 = chat_with_project_identifier(msg1, conversation)
    print(f"User: {msg1}")
    print(f"Assistant: {result1['response']}")
    print(f"Prediction: {result1['prediction']}\n")
    
    # Update history
    conversation.append({"role": "user", "content": msg1})
    conversation.append({"role": "assistant", "content": result1['full_response']})
    
    # Second message
    msg2 = "Yeah, Alice is working on it but she's blocked"
    result2 = chat_with_project_identifier(msg2, conversation)
    print(f"User: {msg2}")
    print(f"Assistant: {result2['response']}")
    print(f"Prediction: {result2['prediction']}\n")


if __name__ == "__main__":
    # Run interactive chat
    interactive_chat()
    
    # Or run the example
    # example_usage()