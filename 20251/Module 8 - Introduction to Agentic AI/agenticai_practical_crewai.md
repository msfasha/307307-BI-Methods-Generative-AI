## Agentic AI Example using CrewAI Library
## 1. Prerequisites & Setup

### Install dependencies

```bash
pip install crewai crewai-tools google-generativeai python-dotenv
```

### Environment variables

Create a `.env` file in your project root:

```
GOOGLE_API_KEY=your_gemini_key_here
```

Then in your code:

```python
import os
from dotenv import load_dotenv
load_dotenv()
gemini_key = os.getenv("GOOGLE_API_KEY")
```

### Gemini SDK setup

```python
import google.generativeai as genai
genai.configure(api_key=gemini_key)

# Example: create a model object
model = genai.GenerativeModel("gemini-1.5-flash")
```

---

## 2. Define a simple “crew” scenario

Let’s assume our objective is:

> **Goal**: “Research recent trends in agentic AI and produce a short summary report.”

We’ll build a crew of two agents:

* A **Researcher** agent: uses web search to collect information
* A **Writer** agent: takes the output of the Researcher and writes the summary

### Tools

We’ll define a simple tool for web search (you could use any search API or simple web scraping). Example placeholder:

```python
from crewai.tools import tool

@tool("Web Search Tool")
def web_search(query: str) -> str:
    # pseudo-implementation: replace with real search logic
    # e.g., use requests + BeautifulSoup or a search API
    return f"Search results for '{query}' …"
```

---

## 3. Define Agents in CrewAI

Using CrewAI’s Python API, you define agents with role, goal, tools, and optionally an LLM override. According to the docs: An Agent has attributes like `role`, `goal`, `backstory`, `llm`, `tools`, etc. ([CrewAI Documentation][1])

Here’s how we might define them:

```python
from crewai import Agent, Crew, Task

# Researcher Agent
researcher = Agent(
    role="Researcher",
    goal="Gather the latest research and articles on agentic AI (2024-2025)",
    backstory="You are a scholarly researcher focused on AI agentic systems.",
    tools=[web_search],
    llm=model,         # using Gemini
    verbose=True
)

# Writer Agent
writer = Agent(
    role="Writer",
    goal="Write a clear summary report of the collected research on agentic AI",
    backstory="You are a technical writer specialising in AI topics.",
    tools=[],
    llm=model,
    verbose=True
)
```

---

## 4. Define Tasks & Crew Workflow

We now define Tasks that agents will execute, and then a Crew to orchestrate them.

```python
# Tasks
task_research = Task(
    description="Research recent trends in agentic AI and list key frameworks, use-cases, and challenges.",
    agent=researcher,
    expected_output="A list of bullet points summarising each trend, with citations/reference links."
)

task_write = Task(
    description="Write a 500-word summary report based on the researcher's findings.",
    agent=writer,
    expected_output="A report titled 'Agentic AI: Trends and Outlook (2024-25)' in Markdown format."
)

# Crew
crew = Crew(
    name="AgenticAI_Crew",
    agents=[researcher, writer],
    tasks=[task_research, task_write]
)
```

You can decide whether tasks are executed sequentially (first research then write) or in parallel; for our scenario we choose sequential.

---

## 5. Running the Crew

Finally, you’ll trigger execution of the crew:

```python
if __name__ == "__main__":
    result = crew.run()
    print("=== Report Output ===")
    print(result[task_write])
```

Under the hood, CrewAI will route the `task_research` to the Researcher agent, whose tools include `web_search`, it uses Gemini as its LLM to reason/plan/use tool, then passes its output into the `task_write` for Writer agent, which uses Gemini to generate the summary.

---

## 6. Example: Researcher Agent Logic

Here’s a snippet showing how the Researcher might perform:

```python
# inside Researcher agent run:
query = "agentic AI recent trends 2025"
search_output = web_search(query)
prompt = f"""You are the Researcher. Using the search output below:
{search_output}

List 5 major trends in agentic AI (2024-2025), each with a short description and one reference link."""
research_results = model.generate_content(prompt).text
```

---

## 7. Example: Writer Agent Logic

```python
# inside Writer agent run:
research_data = crew.context[task_research]  # assume the system passes this
prompt = f"""You are the Writer. Here is the research output:
{research_data}

Write a 500-word summary in Markdown titled “Agentic AI: Trends and Outlook (2024-25)”. Use headings, bullet lists, and ensure readability for a technical audience."""
report = model.generate_content(prompt).text
```

---

## 8. Tips and Best Practices

* Ensure each agent has **clear and narrow role/goal** — avoids confusion. (CrewAI docs emphasise role-based agents) ([CrewAI Documentation][2])
* Provide backstory + context so the model understands its persona.
* Use tools only when necessary; over-injecting many tools into one agent can increase hallucination risk.
* Monitor delegation: CrewAI allows `allow_delegation` so one agent can request help from another. ([Firecrawl - The Web Data API for AI][3])
* Use `verbose=True` during development to inspect agent steps and debug.
* For production, you may want to save outputs, maintain memory (short-term/long-term) and handle errors (timeouts, model failures).
* Use your Gemini key properly and monitor usage/cost of API calls.

---

## 9. Wrap-Up

This tutorial shows how to combine:

* The Gemini model (via Google GenerativeAI SDK) as your reasoning engine
* The CrewAI framework for multi-agent orchestration and workflow management
* Tools integration (e.g., web search) for external information gathering
* Role/goal oriented agents to structure the system reliably

From here you can scale: add more agents (e.g., Editor, Fact-Checker), add memory modules (e.g., vector-store recall), integrate more tools (APIs, databases), and iterate on workflows.

---

[1]: https://docs.crewai.com/en/concepts/agents?utm_source=chatgpt.com "Agents - CrewAI"
[2]: https://docs.crewai.com/concepts/agents?utm_source=chatgpt.com "Agents - CrewAI"
[3]: https://www.firecrawl.dev/blog/crewai-multi-agent-systems-tutorial?utm_source=chatgpt.com "Building Multi-Agent Systems With CrewAI - A Comprehensive Tutorial"

