# pip install python-dotenv google-genai
"""
Minimal agent + tool calling loop.

Demonstrates:
- LLM requesting external information via JSON
- Python executing a function
- LLM continuing after receiving the result
"""

import os
import json
import sys
from dotenv import load_dotenv
from pathlib import Path

# Try to import genai with better error handling
try:
    from google import genai
except ImportError as e:
    print(f"Import error: {e}")
    print("\nTroubleshooting steps:")
    print("1. Make sure you're in your virtual environment (venv)")
    print("2. Run: pip uninstall google-generativeai")
    print("3. Run: pip install --upgrade google-genai")
    print("4. Verify: python -c 'from google import genai; print(\"OK\")'")
    sys.exit(1)
# Load .env from parent directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=api_key)

# -----------------------------------
# Simple external tool (mock weather)
# -----------------------------------
def get_weather(city):
    """
    Mock weather function.
    In real life, this would call an API.
    """
    return f"The weather in {city} is sunny, 25°C."


# -----------------------------------
# Agent prompt
# -----------------------------------
SYSTEM_PROMPT = """
You are an assistant that can answer questions.

If you do NOT have the required information,
you MUST request a function call.

Available function:
get_weather(city)

When requesting a function call, return JSON ONLY
in this format:

{
  "action": "call_function",
  "function": "get_weather",
  "arguments": {
    "city": "<city_name>"
  }
}

If you already have the information, respond normally.
"""

# -----------------------------------
# Agent step
# -----------------------------------
def agent_step(conversation):
    """
    Send conversation to the model and get response.
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=conversation
    )
    return response.text or ""


# -----------------------------------
# Main loop
# -----------------------------------
conversation = SYSTEM_PROMPT
print("Type 'stop' to exit.\n")

while True:
    user_input = input("User> ")

    if user_input.lower() == "stop":
        print("Session ended.")
        break

    # Add user message
    conversation += f"\nUser: {user_input}\nAssistant:"
    print("\nConversation so far:")
    print(conversation)

    # Step 1: Ask the agent
    agent_output = agent_step(conversation)
    print("\nAssistant raw output:")
    print(agent_output)

    # Step 2: Check if the agent is requesting a function
    try:
        data = json.loads(agent_output)
    except Exception:
        # Normal answer, no tool needed
        print("\nAssistant:")
        print(agent_output)
        conversation += agent_output
        continue

    # Step 3: Execute function
    if data.get("action") == "call_function":
        function_name = data["function"]
        arguments = data["arguments"]

        if function_name == "get_weather":
            result = get_weather(arguments["city"])
        else:
            result = "Unknown function."

        # Step 4: Send tool result back to the agent
        conversation += f"\nTool result: {result}\nAssistant:"
        final_response = agent_step(conversation)

        print("\nAssistant:")
        print(final_response)

        conversation += final_response
