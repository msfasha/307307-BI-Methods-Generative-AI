# pip install python-dotenv google-genai
"""
Multi-tool agent demonstration.

Demonstrates:
- Agent with multiple tools (weather, calculator, time, unit converter)
- Tool selection based on user needs
- Clear capability communication to users
"""

import os
import json
import sys
from datetime import datetime
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
# Tool Definitions
# -----------------------------------

def get_weather(city):
    """
    Get weather information for a city.
    In real life, this would call a weather API.
    """
    return f"The weather in {city} is sunny, 25°C."


def calculate(expression):
    """
    Evaluate a mathematical expression safely.
    Examples: "2 + 2", "10 * 5", "100 / 4", "(5 + 3) * 2"
    """
    try:
        # Only allow safe math operations
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Only basic math operations allowed (+, -, *, /, parentheses)"
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating: {e}"


def get_current_time(timezone="UTC"):
    """
    Get the current date and time.
    """
    now = datetime.now()
    return f"Current time ({timezone}): {now.strftime('%Y-%m-%d %H:%M:%S')}"


def convert_units(value, from_unit, to_unit):
    """
    Convert between different units (temperature, length, weight).
    Examples:
    - Temperature: "fahrenheit" to "celsius", "celsius" to "fahrenheit"
    - Length: "miles" to "kilometers", "kilometers" to "miles"
    - Weight: "pounds" to "kilograms", "kilograms" to "pounds"
    """
    conversions = {
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
        ("celsius", "fahrenheit"): lambda x: (x * 9/5) + 32,
        ("miles", "kilometers"): lambda x: x * 1.60934,
        ("kilometers", "miles"): lambda x: x / 1.60934,
        ("pounds", "kilograms"): lambda x: x * 0.453592,
        ("kilograms", "pounds"): lambda x: x / 0.453592,
        ("feet", "meters"): lambda x: x * 0.3048,
        ("meters", "feet"): lambda x: x / 0.3048,
    }
    
    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        result = conversions[key](float(value))
        return f"{value} {from_unit} = {result:.2f} {to_unit}"
    return f"Conversion from {from_unit} to {to_unit} not supported. Available: temperature (fahrenheit/celsius), length (miles/kilometers/feet/meters), weight (pounds/kilograms)"


# -----------------------------------
# Tool Registry
# -----------------------------------
TOOLS = {
    "get_weather": {
        "function": get_weather,
        "description": "Get weather information for a city",
        "arguments": ["city"]
    },
    "calculate": {
        "function": calculate,
        "description": "Perform mathematical calculations",
        "arguments": ["expression"]
    },
    "get_current_time": {
        "function": get_current_time,
        "description": "Get the current date and time",
        "arguments": ["timezone"]
    },
    "convert_units": {
        "function": convert_units,
        "description": "Convert between units (temperature, length, weight)",
        "arguments": ["value", "from_unit", "to_unit"]
    }
}


# -----------------------------------
# Agent System Prompt
# -----------------------------------
SYSTEM_PROMPT = f"""
You are a helpful assistant with access to multiple tools.

Available tools:
1. get_weather(city) - Get weather information for a city
2. calculate(expression) - Perform mathematical calculations (e.g., "2 + 2", "10 * 5")
3. get_current_time(timezone) - Get the current date and time
4. convert_units(value, from_unit, to_unit) - Convert between units
   - Temperature: fahrenheit ↔ celsius
   - Length: miles ↔ kilometers, feet ↔ meters
   - Weight: pounds ↔ kilograms

When you need to use a tool, return ONLY valid JSON (no markdown, no code blocks, no explanations) in this exact format:

{{
  "action": "call_function",
  "function": "<function_name>",
  "arguments": {{
    "<arg1>": "<value1>",
    "<arg2>": "<value2>"
  }}
}}

IMPORTANT: Return ONLY the JSON object, nothing else. Do not wrap it in code blocks or add any text before or after.

For tools with no required arguments (like get_current_time), you can omit arguments or use empty values.

If you already have the information to answer the question, respond normally without using a tool.
"""


# -----------------------------------
# Agent Step Function
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
# JSON Extraction Function
# -----------------------------------
def extract_json_from_response(text):
    """
    Extract JSON from text, handling markdown code blocks.
    """
    text = text.strip()
    
    # Remove markdown code blocks if present
    if text.startswith("```"):
        # Find the first newline after ```
        start_idx = text.find("\n")
        if start_idx != -1:
            text = text[start_idx + 1:]
        # Find the closing ```
        end_idx = text.rfind("```")
        if end_idx != -1:
            text = text[:end_idx]
    
    # Try to find JSON object in the text
    # Look for { ... } pattern
    start_brace = text.find("{")
    end_brace = text.rfind("}")
    
    if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
        json_str = text[start_brace:end_brace + 1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    # If no JSON found, return None
    return None


# -----------------------------------
# Tool Execution Function
# -----------------------------------
def execute_tool(function_name, arguments):
    """
    Execute a tool function with the provided arguments.
    """
    if function_name not in TOOLS:
        return f"Unknown function '{function_name}'. Available functions: {', '.join(TOOLS.keys())}"
    
    tool = TOOLS[function_name]["function"]
    
    try:
        # Handle different argument patterns
        if function_name == "get_weather":
            return tool(arguments.get("city", ""))
        elif function_name == "calculate":
            return tool(arguments.get("expression", ""))
        elif function_name == "get_current_time":
            return tool(arguments.get("timezone", "UTC"))
        elif function_name == "convert_units":
            return tool(
                arguments.get("value", ""),
                arguments.get("from_unit", ""),
                arguments.get("to_unit", "")
            )
        else:
            return "Function execution error"
    except Exception as e:
        return f"Error executing {function_name}: {e}"


# -----------------------------------
# Welcome Message
# -----------------------------------
def print_welcome_message():
    """
    Display agent capabilities to the user.
    """
    print("=" * 70)
    print("🤖 MULTI-TOOL AGENT")
    print("=" * 70)
    print("\nI'm an AI assistant with access to the following tools:\n")
    
    for i, (tool_name, tool_info) in enumerate(TOOLS.items(), 1):
        args_str = ", ".join(tool_info["arguments"])
        print(f"  {i}. {tool_name}({args_str})")
        print(f"     → {tool_info['description']}")
    
    print("\n" + "=" * 70)
    print("Examples of what you can ask:")
    print("  • 'What's the weather in Paris?'")
    print("  • 'Calculate 25 * 4 + 10'")
    print("  • 'What time is it?'")
    print("  • 'Convert 32 fahrenheit to celsius'")
    print("  • 'How many kilometers in 10 miles?'")
    print("=" * 70)
    print("\nType 'stop' to exit.\n")


# -----------------------------------
# Main Loop
# -----------------------------------
def main():
    conversation = SYSTEM_PROMPT
    print_welcome_message()
    
    while True:
        user_input = input("User> ")
        
        if user_input.lower().strip() == "stop":
            print("\nSession ended. Goodbye!")
            break
        
        # Add user message
        conversation += f"\nUser: {user_input}\nAssistant:"
        
        # Step 1: Ask the agent
        agent_output = agent_step(conversation)
        
        # Step 2: Try to extract JSON from response (handles markdown code blocks)
        data = extract_json_from_response(agent_output)
        
        # Step 3: Check if the agent is requesting a function
        if data and data.get("action") == "call_function":
            function_name = data["function"]
            arguments = data.get("arguments", {})
            
            print(f"\n[Agent is using tool: {function_name}]")
            result = execute_tool(function_name, arguments)
            print(f"[Tool result: {result}]")
            
            # Step 4: Send tool result back to the agent
            conversation += f"\nTool result: {result}\nAssistant:"
            final_response = agent_step(conversation)
            
            print(f"\nAssistant: {final_response}")
            conversation += final_response
        else:
            # Normal answer, no tool needed
            print(f"\nAssistant: {agent_output}")
            conversation += agent_output


if __name__ == "__main__":
    main()

