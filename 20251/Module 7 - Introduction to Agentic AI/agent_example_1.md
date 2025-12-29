# Minimal Agent + Tool Loop Example

### (Weather Example – Teaching Version)

---

## Conceptual Flow (one sentence)

> LLM decides → requests tool → Python executes → LLM continues

---

## Full Minimal Code

```python
"""
Minimal agent + tool calling loop.

Demonstrates:
- LLM requesting external information via JSON
- Python executing a function
- LLM continuing after receiving the result
"""

import json
import google.genai as genai

# -----------------------------------
# Configure Gemini
# -----------------------------------
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel("gemini-2.5-flash")

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
    response = model.generate_content(conversation)
    return response.text


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
```

---

## Example Interaction

### User:

```
What is the weather today in Amman?
```

### Assistant (LLM decides it does not know):

```json
{
  "action": "call_function",
  "function": "get_weather",
  "arguments": {
    "city": "Amman"
  }
}
```

### Python executes:

```python
get_weather("Amman")
```

### Tool result:

```
The weather in Amman is sunny, 25°C.
```

### Assistant continues:

```
The weather in Amman today is sunny with a temperature of 25°C.
```

---

## Why this example is **important**

* This is **exactly** how:

  * OpenAI function calling
  * LangChain agents
  * AutoGPT-style systems
  * Production copilots
    actually work under the hood

* The LLM:

  * **Does not execute code**
  * **Does not fetch data**
  * **Requests capabilities**

* Python:

  * Enforces reality
  * Executes safely
  * Feeds results back

---

## Mental Model (remember this)

```
LLM = brain
Tools = hands
Python = nervous system
```
