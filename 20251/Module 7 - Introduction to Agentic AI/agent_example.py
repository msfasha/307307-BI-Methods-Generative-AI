import pandas as pd
import google.generativeai as genai
import json

# Load dataset
df = pd.read_csv("sales.csv")   # Example dataset

# Configure Gemini
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel("gemini-1.5-flash")

# Tools the agent can use
def summary_tool(_):
    return df.describe().to_string()

def correlation_tool(_):
    return df.corr(numeric_only=True).to_string()

tools = {
    "summary": summary_tool,
    "correlation": correlation_tool
}

# Agent decides next action
def agent_decide(state):
    prompt = f"""
You are a data analyst agent. Based on the task and dataset preview below,
choose the best next analytical action.

Return JSON only:
{{"action": "..."}}

State:
{state}
"""
    return model.generate_content(prompt).text

def execute(action_json):
    data = json.loads(action_json)
    action = data["action"]

    if action in tools:
        return tools[action](None)
    else:
        return "Unknown action"

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
Based on the updated state, produce a short, clear explanation of the insights.
"""

final_answer = model.generate_content(final_prompt).text

print("\nFinal Insight Report:\n", final_answer)
