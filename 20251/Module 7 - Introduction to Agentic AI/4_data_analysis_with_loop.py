"""
Simple tool-using agent with Gemini.

Capabilities:
- Runs in a loop until user types 'stop'
- Agent selects one tool using JSON
- Python validates and executes tools
- Supports:
  - Dataset summary
  - Correlation matrix
  - Descriptive statistics for a single column
"""

import pandas as pd
import json
import os
from pathlib import Path
from dotenv import load_dotenv

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
    exit(1)

# Load .env from parent directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

# -------------------------------------------------
# Load dataset
# -------------------------------------------------
# Get the directory where this script is located
script_dir = Path(__file__).resolve().parent
df = pd.read_csv(script_dir / "sales.csv")

# -------------------------------------------------
# Configure Gemini
# -------------------------------------------------
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set in .env file")

client = genai.Client(api_key=api_key)

# -------------------------------------------------
# Tool implementations
# -------------------------------------------------
def summary_tool(_):
    """
    Return descriptive statistics for the entire dataset.
    """
    return df.describe().to_string()


def correlation_tool(_):
    """
    Return correlation matrix for numeric columns.
    """
    return df.corr(numeric_only=True).to_string()


def describe_column_tool(column_name):
    """
    Return descriptive statistics for a single column.
    Works for both numeric and categorical columns.
    """
    if column_name not in df.columns:
        return (
            f"Column '{column_name}' does not exist.\n"
            f"Available columns: {list(df.columns)}"
        )

    return df[column_name].describe().to_string()


# -------------------------------------------------
# Tool registry
# -------------------------------------------------
tools = {
    "summary": summary_tool,
    "correlation": correlation_tool,
    "describe_column": describe_column_tool
}

TOOL_LIST_TEXT = ", ".join(tools.keys())

# -------------------------------------------------
# JSON Extraction Function
# -------------------------------------------------
def extract_json_from_response(text):
    """
    Extract JSON from text, handling markdown code blocks.
    """
    if not text:
        return None
        
    text = text.strip()
    
    # Remove markdown code blocks if present (handles ```json or just ```)
    if text.startswith("```"):
        # Find the first newline after ``` (could be ```json or just ```)
        lines = text.split("\n")
        if len(lines) > 1:
            # Skip the first line (```json or ```) and get the rest
            text = "\n".join(lines[1:])
        # Find and remove the closing ```
        if text.endswith("```"):
            text = text[:-3].strip()
        else:
            # Find closing ``` in the middle
            end_idx = text.rfind("```")
            if end_idx != -1:
                text = text[:end_idx].strip()
    
    # Try to find JSON object in the text
    # Look for { ... } pattern
    start_brace = text.find("{")
    end_brace = text.rfind("}")
    
    if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
        json_str = text[start_brace:end_brace + 1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            # If parsing fails, try to clean up the string more
            # Remove any leading/trailing whitespace from the JSON string
            json_str = json_str.strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
    
    # If no JSON found, return None
    return None


# -------------------------------------------------
# Agent decision logic
# -------------------------------------------------
def agent_decide(state, user_input):
    """
    Ask the model to decide which tool to use.
    The model must respond with JSON only.
    """
    available_actions = ", ".join(tools.keys())
    prompt = f"""
You are a data analyst agent.

IMPORTANT: You can ONLY use these available tools:
{available_actions}

- "summary" - Get descriptive statistics for the entire dataset
- "correlation" - Get correlation matrix for numeric columns
- "describe_column" - Get descriptive statistics for a specific column (requires column name in "argument" field)

If no tool applies, use action "none".

You MUST choose one of these actions. Do NOT suggest other actions that are not available.

Return JSON ONLY (no markdown, no code blocks) in this format:
{{
  "action": "<tool_name_or_none>",
  "argument": "<column_name_or_empty>"
}}

Conversation state:
{state}

User request:
{user_input}
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text or ""


# -------------------------------------------------
# Safe tool execution
# -------------------------------------------------
def execute(action_json):
    """
    Execute a known tool after validating the agent response.
    """
    # Try to extract JSON from response (handles markdown code blocks)
    data = extract_json_from_response(action_json)
    
    if not data:
        # Try direct parsing as fallback (only if extraction completely failed)
        try:
            # Strip whitespace first
            cleaned = action_json.strip()
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            # Show a helpful error message
            preview = action_json[:200] if len(action_json) > 200 else action_json
            return f"Error: Could not parse JSON from response. Preview: {preview}..."
    
    if not data:
        return f"Error: Could not extract JSON from response: {action_json[:100]}..."
    
    action = data.get("action")
    argument = data.get("argument", "")

    if action == "none":
        return "No tool execution required."

    if action not in tools:
        return (
            f"Unknown tool '{action}'.\n"
            f"I can only use the following tools: {TOOL_LIST_TEXT}"
        )

    if action == "describe_column":
        if not argument:
            return "describe_column requires a column name."
        return tools[action](argument)

    # Tools without arguments
    return tools[action](None)


# -------------------------------------------------
# Welcome Message
# -------------------------------------------------
def print_welcome_message():
    """
    Display agent capabilities to the user.
    """
    print("=" * 70)
    print("📊 DATA ANALYSIS AGENT")
    print("=" * 70)
    print("\nI'm an AI assistant that can analyze your sales dataset.")
    print("I have access to the following analytical tools:\n")
    
    print("  1. summary")
    print("     → Get descriptive statistics for the entire dataset")
    print("     → Shows count, mean, std, min, max, quartiles for all numeric columns\n")
    
    print("  2. correlation")
    print("     → Get correlation matrix for numeric columns")
    print("     → Shows how numeric variables relate to each other\n")
    
    print("  3. describe_column")
    print("     → Get descriptive statistics for a specific column")
    print("     → Works for both numeric and categorical columns")
    print("     → Usage: Ask about a specific column name\n")
    
    print("=" * 70)
    print("Examples of what you can ask:")
    print("  • 'Show me summary statistics'")
    print("  • 'What are the correlations?'")
    print("  • 'Describe the UnitsSold column'")
    print("  • 'Give me statistics for UnitPrice'")
    print("=" * 70)
    print("\nDataset Info:")
    print(f"  • Rows: {len(df)}")
    print(f"  • Columns: {list(df.columns)}")
    print(f"\nData preview:")
    print(df.head().to_string())
    print("\n" + "=" * 70)
    print("Type 'stop' to end the session.\n")


# -------------------------------------------------
# Initial shared state
# -------------------------------------------------
state = f"""
Goal: Provide insights about the sales dataset.

Data preview:
{df.head().to_string()}
"""

print_welcome_message()

# -------------------------------------------------
# Main interaction loop
# -------------------------------------------------
while True:
    user_input = input("User> ")

    if user_input.lower().strip() == "stop":
        print("Session ended.")
        break

    # Step 1: Agent chooses action
    decision = agent_decide(state, user_input)
    print("\nAgent decision:")
    print(decision)

    # Step 2: Execute tool
    observation = execute(decision)
    print("\nObservation:")
    print(observation)

    # Step 3: Update state
    state += f"""
User request:
{user_input}

Agent decision:
{decision}

Observation:
{observation}
"""
