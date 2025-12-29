# pip install pandas google-genai python-dotenv

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

# Get the directory where this script is located
script_dir = Path(__file__).resolve().parent

# Load dataset using the script's directory
df = pd.read_csv(script_dir / "sales.csv")   # Example dataset

# Configure Gemini client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set in .env file")

client = genai.Client(api_key=api_key)

# Tools the agent can use
def summary_tool(_):
    return df.describe().to_string()

def correlation_tool(_):
    return df.corr(numeric_only=True).to_string()

tools = {
    "summary": summary_tool,
    "correlation": correlation_tool
}

# -----------------------------------
# JSON Extraction Function
# -----------------------------------
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


# Agent decides next action
def agent_decide(state):
    available_actions = ", ".join(tools.keys())
    prompt = f"""
You are a data analyst agent. Based on the task and dataset preview below,
choose the best next analytical action.

IMPORTANT: You can ONLY use these available actions:
{available_actions}

- "summary" - Get descriptive statistics for the entire dataset
- "correlation" - Get correlation matrix for numeric columns

You MUST choose one of these actions. Do NOT suggest other actions that are not available.

Return JSON only (no markdown, no code blocks):
{{"action": "<one_of_the_available_actions>"}}

State:
{state}
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text or ""

def execute(action_json):
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
    
    if not action:
        return "Error: No 'action' field in JSON response"
    
    if action in tools:
        return tools[action](None)
    else:
        return f"Unknown action: '{action}'. Available actions: {', '.join(tools.keys())}"

# Initial state includes task + preview of data
state = f"""
Goal: Provide insights about the sales dataset.
Data preview:
{df.head().to_string()}
"""

# Step 1: Agent chooses action
decision = agent_decide(state)
print("Model decision:", decision)

# Step 2: Python executes tool
observation = execute(decision)

# Update state
state += f"\nExecuted: {decision}\nObservation:\n{observation}"

# Step 3: Agent provides final insights
final_prompt = f"""
You are a senior data analyst.
Based on the updated state below, produce a short, clear explanation of the insights.

IMPORTANT: Return plain text only. Do NOT use markdown formatting (no **, no ##, no lists with * or -). 
Just write in simple, clear sentences.

Updated State:
{state}
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=final_prompt
)
final_answer = response.text or ""

print("\nFinal Insight Report:\n", final_answer)
