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
import google.genai as genai
import json

# -------------------------------------------------
# Load dataset
# -------------------------------------------------
df = pd.read_csv("sales.csv")

# -------------------------------------------------
# Configure Gemini
# -------------------------------------------------
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel("gemini-2.5-flash")

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
# Agent decision logic
# -------------------------------------------------
def agent_decide(state, user_input):
    """
    Ask the model to decide which tool to use.
    The model must respond with JSON only.
    """
    prompt = f"""
You are a data analyst agent.

You can ONLY use the following tools:
{TOOL_LIST_TEXT}

If no tool applies, use action "none".

Return JSON ONLY in this format:
{{
  "action": "<tool_name_or_none>",
  "argument": "<column_name_or_empty>"
}}

Conversation state:
{state}

User request:
{user_input}
"""
    return model.generate_content(prompt).text


# -------------------------------------------------
# Safe tool execution
# -------------------------------------------------
def execute(action_json):
    """
    Execute a known tool after validating the agent response.
    """
    try:
        data = json.loads(action_json)
        action = data.get("action")
        argument = data.get("argument")
    except Exception:
        return "Invalid JSON returned by the agent."

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
# Initial shared state
# -------------------------------------------------
state = f"""
Goal: Provide insights about the sales dataset.

Data preview:
{df.head().to_string()}
"""

print("Type 'stop' to end the session.\n")

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
