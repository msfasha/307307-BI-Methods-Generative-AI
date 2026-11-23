# Module 6 — Introduction to CrewAI (Lecture Notes)
**Course:** 307307 BI Methods for Generative AI — *Agentic AI half* | **University of Petra**

> In Modules 1–5 we built an agent by hand: the loop, memory, tools, planning. **CrewAI** is a framework that packages those pieces so you describe *what you want* and it runs the loop for you. This page explains CrewAI's components **one at a time**, each level adding exactly one idea to the one before. Read it before the lab, then keep it open while you work through the lab steps.

## Learning Objectives
By the end of this module you should be able to:
- Name CrewAI's building blocks (**Agent, Task, Crew, Tool, Flow**) and say what each is for.
- Explain what `expected_output`, `context` and `{placeholders}` do in a Task.
- Write a tool the agent can call, and explain why its docstring matters.
- Explain `@start`, `@listen` and `@router` in a Flow, and trace the order in which steps run.
- Decide when to use a **Crew** (agents figure it out) and when to use a **Flow** (you control the order).

## The ladder at a glance

| Level | New idea | Component | Lab step |
|---|---|---|---|
| 0 | An agent is an LLM + persona + (optional) tools + a loop | `Agent` | Step 1 |
| 1 | A job with a definition of "done" | `Task`, `Crew` | Step 1 |
| 2 | Several agents passing work along | `Process.sequential`, `context`, `{inputs}` | Step 4 |
| 3 | Let agents *act* | `@tool` | Step 3 |
| 4 | Make output usable by code | `output_pydantic` | Step 2 |
| 5 | You control the order | `Flow`, `@start`, `@listen`, `@router` | Step 9 |
| 6 | Flow as the skeleton, Crews as the brains | Flow + Crew | Step 9 |

Each code block below is short and self-contained. The lab then applies the same ideas to one running example (the fictional *Petra Bean* coffee shop).

## Setup
```bash
pip install 'crewai[tools,google-genai]'     # the lab uses Gemini; use [openai] or [anthropic] for those
export GOOGLE_API_KEY=...
```
The extra in the brackets installs the provider you choose. Without it CrewAI raises an import error when it first calls the model.

## Level 0 — What is an "agent"?
An agent is an LLM with three things attached:
- a **role / goal / backstory** — a persona written into its system prompt (think: a job description);
- optional **tools** it can call (Level 3);
- a **loop** — it thinks, calls a tool if needed, reads the result, and repeats until it can answer. This is the THOUGHT → ACTION → OBSERVATION loop from Module 4, written for you.

```python
from crewai import Agent, LLM

llm = LLM(model="gemini/gemini-3.6-flash")

analyst = Agent(
    role="Market Analyst",
    goal="Give short, accurate answers about markets",
    backstory="You are a careful analyst who admits uncertainty.",
    llm=llm,
)

result = analyst.kickoff("What is a P/E ratio?")
print(result.raw)
```
`kickoff()` runs the agent once. No Task or Crew is needed yet. If you only need one agent answering questions, you can stop here.

## Level 1 — Task and Crew (one agent, one job)
A **Task** is a specific piece of work. Unlike a chat message it has an **`expected_output`**, which tells the agent what "done" looks like. A **Crew** is the container that runs tasks.

```python
from crewai import Agent, Task, Crew

writer = Agent(role="Explainer", goal="Explain topics simply",
               backstory="You teach beginners.", llm=llm)

explain = Task(
    description="Explain what an API is to a 12-year-old.",
    expected_output="Exactly 3 sentences, with one analogy.",
    agent=writer,
)

crew = Crew(agents=[writer], tasks=[explain])
print(crew.kickoff().raw)
```
**Try it:** change `expected_output` and watch the answer change. It is the single biggest lever you have.

| Component | Answers the question |
|---|---|
| **Agent** | *Who* is doing the work? |
| **Task** | *What* exactly must be done, and what does a good result look like? |
| **Crew** | *Which* agents and tasks, and *how* do they run together? |

## Level 2 — Two agents passing work along
By default a crew runs its tasks one after another (`Process.sequential`), like an assembly line. Earlier outputs are passed along to later tasks, and `context` lets you say explicitly which ones.

```python
from crewai import Process

researcher = Agent(role="Researcher", goal="List accurate facts",
                   backstory="Thorough and skeptical.", llm=llm)
writer = Agent(role="Writer", goal="Write crisp summaries",
               backstory="Writes for busy executives.", llm=llm)

research = Task(
    description="List 5 facts about {topic}.",
    expected_output="A bulleted list of 5 facts.",
    agent=researcher,
)
write = Task(
    description="Turn the facts into a 50-word summary.",
    expected_output="One paragraph, max 50 words.",
    agent=writer,
    context=[research],            # the writer receives the researcher's output
)

crew = Crew(agents=[researcher, writer], tasks=[research, write],
            process=Process.sequential)
print(crew.kickoff(inputs={"topic": "solar power"}).raw)
```
Two new ideas:
- **`{topic}`** is a placeholder. Its value comes from `inputs={...}` at kickoff, so one crew can be reused for any topic.
- **`context=[research]`** says the writer receives the researcher's output.

## Level 3 — Tools (let agents act)
A **tool** is a Python function the agent may decide to call. The agent never sees your code: it sees the tool's **name, type hints and docstring**. That text is how it decides *whether* and *how* to use the tool.

```python
from crewai.tools import tool

@tool("Word counter")
def word_count(text: str) -> str:
    """Count the number of words in the given text."""
    return str(len(text.split()))

editor = Agent(role="Editor", goal="Enforce length limits",
               backstory="Strict about word counts.",
               tools=[word_count], llm=llm)
```
If an agent misuses a tool, a vague docstring is the usual cause. You can test a tool without any LLM: `word_count.run(text="one two three")` returns `"3"`. CrewAI also ships ready-made tools in `crewai_tools` (web search, file reading, scraping).

This is the *intent vs action* idea from Module 4: the model only *asks* for the tool; CrewAI runs it and hands the result back.

## Level 4 — Structured output
Free text is hard to use in code. Make the task return a typed object instead:

```python
from pydantic import BaseModel

class Brief(BaseModel):
    title: str
    bullets: list[str]

write = Task(
    description="Summarize solar power.",
    expected_output="A title and 3 bullets.",
    agent=writer,
    output_pydantic=Brief,
)

result = Crew(agents=[writer], tasks=[write]).kickoff()
print(result.pydantic.title)       # a real Python object, not a paragraph
```
Use this whenever a later step (an `if`, a database, a chart) needs a specific field such as a verdict.

## Level 5 — Flows: `@start`, `@listen`, `@router`
Crews are good when you want agents to *figure things out*. Sometimes you want to control the order yourself: do this, then that, and *if* X then do Y. That is a **Flow**.

A Flow is an ordinary Python class where **each method is a step**. Decorators say *when* a step runs:

| Decorator | Meaning |
|---|---|
| `@start()` | "Run this when the flow begins." The entry point. A flow may have several. |
| `@listen(step)` | "Run this when `step` finishes." It also receives `step`'s return value. |
| `@router(step)` | "Run after `step`, then **choose a path** by returning a text label." |
| `@listen("label")` | "Run when a router returns this label." |

Think of dominoes: `@start` tips the first one and `@listen` says which domino falls after which. `self.state` is memory shared by all steps. Here is a Flow with **no AI in it**, so you see only the mechanics:

```python
from crewai.flow.flow import Flow, start, listen, router
from pydantic import BaseModel

class S(BaseModel):
    n: int = 0

class Demo(Flow[S]):
    @start()
    def begin(self):
        print("1. begin")
        self.state.n = 7                  # shared memory for the whole flow
        return "from-begin"

    @listen(begin)
    def second(self, prev):               # prev = begin's return value
        print("2. second got:", prev)
        return "from-second"

    @listen(second)
    def third(self, prev):
        print("3. third got:", prev, "state.n =", self.state.n)

    @router(second)                       # chooses a path by returning a label
    def decide(self):
        return "big" if self.state.n > 5 else "small"

    @listen("big")                        # listens to a label, not a method
    def on_big(self):
        print("4. router chose BIG")

    @listen("small")
    def on_small(self):
        print("4. router chose SMALL")

Demo().kickoff()
```
Output:
```
1. begin
2. second got: from-begin
3. third got: from-second state.n = 7
4. router chose BIG
```
How to read it: `begin` runs first (`@start`). `second` runs after it and receives `"from-begin"`. `third` runs after `second`. The router also runs after `second`; it returns `"big"` or `"small"`, and **only** the method listening for that label runs. That is your if/else.

**Waiting for several steps.** `and_` waits for all, `or_` fires on the first:
```python
from crewai.flow.flow import and_, or_

class D(Flow):
    @start()
    def a(self): print("a")
    @start()
    def b(self): print("b")

    @listen(and_(a, b))                   # runs only after BOTH finish
    def both(self): print("both a AND b done")
```
Prints `a`, `b`, then `both a AND b done`. With `or_(a, b)` it would run as soon as either finishes.

## Level 6 — Putting it together: a Flow that calls a Crew
Each Flow step can be plain Python, a single LLM call, or a whole Crew. The usual production pattern is **a Flow for the skeleton, Crews for the thinking**:

```python
class S(BaseModel):
    topic: str = ""

class BriefFlow(Flow[S]):
    @start()
    def get_topic(self):
        self.state.topic = "solar power"          # could come from user input

    @listen(get_topic)
    def run_crew(self):
        crew = Crew(agents=[researcher, writer], tasks=[research, write])
        return crew.kickoff(inputs={"topic": self.state.topic}).raw

    @listen(run_crew)
    def save(self, brief):
        open("brief.md", "w").write(brief)
```
The lab's Step 9 does exactly this: a cheap one-agent check first, a router that stops early on a "no-go", and the full team only if the idea passes.

## Crew or Flow? How to choose

| | **Crew** | **Flow** |
|---|---|---|
| Who decides the order? | The agents (or a manager agent) | You, in code |
| Strength | Open-ended work, flexible reasoning | Predictable, cheap, auditable |
| Weakness | Less predictable, more tokens | You must foresee the steps |
| Use for | "Research this and write a memo" | "Check first; only then spend on the full team" |

In practice you combine them. This is also a **governance** point: a Flow gives you a fixed, reviewable path with explicit stopping rules, which is much easier to audit than free agent behaviour.

## Beyond the ladder (covered in the lab)
Once the ladder is clear, the lab adds the production features on top of it: **knowledge** (documents the crew can search), **memory** (facts kept between runs), **guardrails and human review** (checks on output), and a **hierarchical process** where a manager agent delegates. Each is one extra argument on the Agent, Task or Crew you already know.

## Check yourself
1. In the Level 5 example, if `state.n` were `3` instead of `7`, which of `on_big` and `on_small` would run, and would `third` still run?
2. What does `context=[research]` do, and what happens if you leave it out?
3. Why does a tool's docstring matter?
4. When would you choose a Flow over a Crew?

<details>
<summary>Answers</summary>

1. `on_small` runs (the router returns `"small"`, so nothing listens for `"big"`), and `third` **still runs**: it listens to `second`, not to the router, so the routing decision does not affect it.
2. It gives the writer the researcher's output as input. A sequential crew already passes earlier results along by default, so leaving it out often still works, but `context` makes the dependency explicit and lets you choose exactly which tasks feed which.
3. It is the only description the LLM has of what the tool does and how to call it. A vague docstring leads to the tool being ignored or misused.
4. When the order or the stopping rules must be predictable, cheap or auditable, and you can write them down in advance.
</details>

## Where to practice
1. Run Level 0, then change the persona and see how the answer shifts.
2. Build Level 2 with a topic you care about, then break it with a vague `expected_output`.
3. Add a custom tool, for example one that reads a local file (the lab's Exercise 2 does this).
4. Rebuild Level 5 with your own made-up steps and a router, then open the lab at Step 9.
