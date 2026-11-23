# Module 6 — Introduction to CrewAI (Lecture Notes)
**Course:** 307307 BI Methods for Generative AI — *Agentic AI half* | **University of Petra**

> In Modules 1–5 we built an agent by hand: the loop, memory, tools, planning. **CrewAI** is a framework that packages those pieces so you describe *what you want* and it runs the loop for you. This page explains CrewAI's components **one at a time**, each level adding exactly one idea to the one before. Read it before the lab, then keep it open while you work through the lab steps.

## Learning Objectives
By the end of this module you should be able to:
- Name CrewAI's building blocks (**Agent, Task, Crew, Tool, Flow**) and say what each is for.
- Explain what `expected_output`, `context` and `{placeholders}` do in a Task.
- Write a tool the agent can call, and explain why its docstring matters.
- Explain `@start`, `@listen` and `@router` in a Flow, and trace the order in which steps run.
- Explain the **philosophy** behind CrewAI: a company-like team, declared not coded, with both autonomy and control.
- Decide when to use a **Crew** (agents figure it out) and when to use a **Flow** (you control the order).

## The philosophy of CrewAI: why it looks the way it does

Before the code, it helps to understand the **idea** the designers had. Once you see it, every class and every argument in the library becomes predictable. (This is our reading of the design, drawn from how the library is built; it is a way to understand it, not an official statement.)

### Idea 1: Model an AI system like a small company
In Modules 1 to 5 we built one agent by hand and wrote its loop ourselves. CrewAI starts from a different observation: **we already know how to organise people to do complex work.** We hire specialists, give each a job description, hand out work orders, and let them pass results along. So CrewAI gives you the same vocabulary:

| In a company | In CrewAI |
|---|---|
| An employee with a job title and experience | **Agent** (`role`, `goal`, `backstory`) |
| A work order: what to do, what the deliverable looks like | **Task** (`description`, `expected_output`) |
| A team or department | **Crew** |
| The way work moves (assembly line, or a manager delegating) | **Process** (`sequential` or `hierarchical`) |
| The equipment employees may use | **Tools** |
| The company handbook / the team's notebook | **Knowledge** / **Memory** |
| The standard operating procedure | **Flow** |

This is why the code reads almost like a staffing plan, and why you can explain a crew to a non-programmer.

### Idea 2: Declare *what* you want, not *how* to loop
When we wrote `TinyAgent` we coded the THOUGHT, ACTION, OBSERVATION loop ourselves. In CrewAI that loop is **built in**. You **declare** who the agent is, what the task is and what a good answer looks like, and the framework handles prompting, calling tools, retrying and passing results to the next agent. The price of this convenience is that the framework builds the prompts for you (we printed one in the Agent section), so you must learn which boxes influence which part of the prompt.

### Idea 3: Specialists beat generalists
One model asked to "research, analyse and write the report" tends to do everything shallowly. Splitting the job among agents with **narrow, clearly written roles** and a **reviewable output at each step** usually gives better and more checkable results. Each agent sees only what its task needs. The cost is real: more agents means more model calls, more tokens and more waiting (the long lab measures this).

### Idea 4: Two kinds of control, autonomy *and* determinism
This is the most important idea, and the reason CrewAI has two main building blocks:

| | **Crew** (autonomy) | **Flow** (determinism) |
|---|---|---|
| Philosophy | "Here is the goal and the team; **figure it out**." | "Here is the procedure; **follow it exactly**." |
| Order decided by | the agents (or a manager agent) | **your Python code** |
| Strength | flexible, handles open-ended problems | predictable, cheap, auditable |
| Weakness | can wander, costs more, harder to predict | you must know the steps in advance |

CrewAI's position is that real applications need **both**: a Flow supplies the dependable skeleton (checks, branches, stopping rules, saving results) and Crews supply intelligence inside the steps where judgement is needed. Let the model think where thinking helps; use ordinary code where certainty matters.

### Idea 5: Make results something other code can trust
A paragraph is fine for a person but useless for a program. So CrewAI puts the **definition of done** into the Task (`expected_output`), lets you demand a **typed object** (`output_pydantic`), lets you add **guardrails** that reject bad answers, and lets a **human approve** (`human_input`). The philosophy: *a model's output is a draft until something checks it.*

### Idea 6: Batteries included
Tools, knowledge (searchable documents), memory (remembering between runs), delegation, many model providers behind one `LLM(...)` line: you assemble these as options on the objects you already know rather than writing glue code. The aim is a **fast path from idea to working prototype**.

### Honest trade-offs
A good engineer knows when *not* to use a tool:
- **Cost and speed.** Every agent runs its own thinking loop. A crew is often 5 to 20 times more expensive than a single model call. Use it when the quality gain is worth it.
- **Unpredictability.** Models are not deterministic. The same crew can give different answers on two runs. Flows, guardrails and structured output exist precisely to contain this.
- **Hidden prompts.** Convenience means the framework writes parts of the prompt for you. When results are odd, inspect the prompt and the verbose log.
- **Not always needed.** A single well-written prompt, or one agent with one tool, solves many problems. Add agents only when there is a real reason (different skills, a need for review, steps that must be checked).

**Rule of thumb:** *start with the smallest thing that works (one agent), add a tool when facts matter, add a second agent when a different skill or a reviewer is needed, and wrap it all in a Flow when the process must be predictable.* That is exactly the order of the parts in this material.

### Questions to think about
1. Which of the six ideas explains why a Task has an `expected_output` box?
2. A bank wants an AI system that approves loans. Which parts would you give to a Crew and which to a Flow, and why?
3. Name a task where a single prompt is better than a crew.

## The ladder at a glance

Each level adds **one** idea. The code in the notes is **the same code as in the *CrewAI Basics* lab** (Parts 1 to 7), so you can read here and run there.

| Level | New idea | Component | Basics lab part | Long lab step |
|---|---|---|---|---|
| 0 | An agent is an LLM + persona (+ tools) + a loop | `Agent` | Part 1 | Step 1 |
| 1 | A job with a definition of "done" | `Task`, `Crew` | Part 2 | Step 1 |
| 2 | Several agents passing work along | `Process.sequential`, `context`, `{inputs}` | Part 3 | Step 4 |
| 3 | Let agents *act* | `@tool` | Part 4 | Step 3 |
| 4 | Make output usable by code | `output_pydantic` | Part 5 | Step 2 |
| 5 | You control the order | `Flow`, `@start`, `@listen`, `@router` | Part 6 | Step 9 |
| 6 | Flow as the skeleton, Crews as the brains | Flow + Crew | Part 7 | Step 9 |

## Setup
```bash
pip install 'crewai[google-genai]'     # the labs use Gemini; use [openai] or [anthropic] for those
export GOOGLE_API_KEY=...
```
The extra in the brackets installs the provider you choose. Without it CrewAI raises an import error when it first calls the model.

```python
from crewai import Agent, Task, Crew, Process, LLM
llm = LLM(model="gemini/gemini-3.6-flash")   # "gemini/" selects Google Gemini
```

## Level 0 — What is an "agent"? (Basics Part 1)
An agent is an LLM with three things attached:
- a **role / goal / backstory**: a persona written into its system prompt (a job description);
- optional **tools** it can call (Level 3);
- a **loop**: think, call a tool if needed, read the result, repeat until it can answer (the THOUGHT, ACTION, OBSERVATION loop of Module 4, written for you).

```python
guide = Agent(
    role="Student Travel Guide",
    goal="Give short, practical travel advice to students on a small budget",
    backstory="You have backpacked across 40 countries and you always think about cost first.",
    llm=llm,
)

answer = guide.kickoff("I have 2 days in Amman. What should I see?")
print(answer.raw)
```
`kickoff()` runs the agent once. No Task or Crew is needed yet. If you only need one agent answering questions, you can stop here.

## Level 1 — Task and Crew (Basics Part 2)
A **Task** is a specific piece of work with an **`expected_output`** that says what "done" looks like. A **Crew** is the container that runs tasks.

```python
explain = Task(
    description="Explain what an API is to a 12-year-old.",
    expected_output="Exactly 3 sentences, including one everyday analogy.",
    agent=guide,
)

crew = Crew(agents=[guide], tasks=[explain])
result = crew.kickoff()
print(result.raw)
```
**Try it:** change `expected_output` and watch the answer change. It is your strongest lever.

| Component | Answers the question |
|---|---|
| **Agent** | *Who* is doing the work? |
| **Task** | *What* exactly, and what does a good result look like? |
| **Crew** | *Which* agents and tasks, and *how* do they run together? |

Look inside what `kickoff()` returns:
```python
# kickoff returns a result object. Look inside it (this reuses `result` from the cell above).
print("Type of result:", type(result).__name__)
print("--- result.raw (the final answer as text) ---")
print(result.raw)
print("--- result.tasks_output (one entry per task) ---")
for t in result.tasks_output:
    print("*", t.description, "->", t.raw[:80], "...")
print("--- result.token_usage (how much text was consumed) ---")
print(result.token_usage)
```

## Level 2 — Several agents passing work along (Basics Part 3)
A crew runs its tasks one after another (`Process.sequential`), like an assembly line. Earlier outputs are passed along, and `context` says explicitly which ones.
- **`{topic}`** is a placeholder; its value comes from `inputs={...}` at kickoff, so one crew serves any topic.
- **`context=[research]`** says the writer receives the researcher's output.

```python
researcher = Agent(
    role="Researcher",
    goal="List accurate, relevant facts",
    backstory="Thorough and sceptical. You never invent facts.",
    llm=llm,
)
writer = Agent(
    role="Writer",
    goal="Write crisp summaries for busy managers",
    backstory="You write short, clear business prose.",
    llm=llm,
)

research = Task(
    description="List 5 facts about {topic}.",
    expected_output="A bulleted list of 5 facts.",
    agent=researcher,
)
write = Task(
    description="Turn the facts into a summary for a manager.",
    expected_output="One paragraph of at most 50 words.",
    agent=writer,
    context=[research],        # the writer receives the researcher's output
)

team = Crew(agents=[researcher, writer], tasks=[research, write], process=Process.sequential)

print(team.kickoff(inputs={"topic": "solar power in Jordan"}).raw)
```

## Level 3 — Tools (Basics Part 4)
A **tool** is a Python function the agent may decide to call. The agent never sees your code: it sees the tool's **name, type hints and docstring**. That text is how it decides *whether* and *how* to use the tool (details in the reference section below).

```python
from crewai.tools import tool

@tool("Add VAT")
def add_vat(price: float, vat_percent: float) -> str:
    """Calculate the final price after adding VAT (sales tax).
    Inputs: the price before tax, and the VAT rate as a percentage (for example 16 for 16%).
    Returns the price including VAT, rounded to 2 decimals."""
    return str(round(price * (1 + vat_percent / 100), 2))

# You can test a tool directly, with no AI involved:
print(add_vat.run(price=80, vat_percent=16))
```
Give it to an agent (the only change is `tools=[...]`):
```python
shopper = Agent(
    role="Shopping Assistant",
    goal="Answer price questions exactly, never guessing a number you can calculate",
    backstory="You help customers understand what they will really pay.",
    tools=[add_vat],
    llm=llm,
    verbose=True,
)

price_task = Task(
    description="A laptop costs 849.50 before tax. VAT is 16%. What is the final price?",
    expected_output="One sentence stating the final price.",
    agent=shopper,
)

print(Crew(agents=[shopper], tasks=[price_task]).kickoff().raw)
```
This is the *intent vs action* idea from Module 4: the model only *asks* for the tool; CrewAI runs it and hands the result back.

## Level 4 — Structured output (Basics Part 5)
Free text is hard to use in code. Make the task return a typed object instead, so a later `if`, database or chart can read a field:

```python
from typing import List, Literal
from pydantic import BaseModel

class TripVerdict(BaseModel):
    worth_it: Literal["yes", "maybe", "no"]    # only these three values are allowed
    reasons: List[str]

verdict_task = Task(
    description="A student asks: is a 1-day trip from Amman to Petra worth the cost?",
    expected_output="A verdict (yes, maybe or no) and 2 to 3 short reasons.",
    agent=guide,
    output_pydantic=TripVerdict,
)

out = Crew(agents=[guide], tasks=[verdict_task]).kickoff()

print(out.pydantic.worth_it)       # a real Python value, usable in an if-statement
print(out.pydantic.reasons)
```

## Level 5 — Flows: `@start`, `@listen`, `@router` (Basics Part 6)
Crews are good when agents should *figure things out*. When **you** want to control the order (do this, then that, and *if* X then Y), use a **Flow**: a normal Python class where **each method is a step**.

| Decorator | Meaning |
|---|---|
| `@start()` | "Run this when the flow begins." The entry point. A flow may have several. |
| `@listen(step)` | "Run this when `step` finishes." It also receives `step`'s return value. |
| `@router(step)` | "Run after `step`, then **choose a path** by returning a text label." |
| `@listen("label")` | "Run when a router returns this label." |

Think of dominoes: `@start` tips the first one and `@listen` says which falls next. `self.state` is memory shared by all steps. This flow has **no AI in it**, so you see only the mechanics:

```python
from crewai.flow.flow import Flow, start, listen, router
from pydantic import BaseModel

class OrderState(BaseModel):
    amount: float = 0

class OrderFlow(Flow[OrderState]):

    @start()
    def receive_order(self):
        print("1. order received")
        self.state.amount = 250          # shared memory for the whole flow
        return "order-17"

    @listen(receive_order)
    def log_order(self, order_id):       # gets receive_order's return value
        print("2. logging", order_id, "amount =", self.state.amount)

    @router(receive_order)
    def check_amount(self):
        return "needs_approval" if self.state.amount > 100 else "auto_approve"

    @listen("needs_approval")
    def ask_manager(self):
        print("3. amount is large, a manager must approve")

    @listen("auto_approve")
    def approve(self):
        print("3. small amount, approved automatically")

OrderFlow().kickoff()
```
Output:
```
1. order received
2. logging order-17 amount = 250
3. amount is large, a manager must approve
```
How to read it: `receive_order` runs first (`@start`). `log_order` runs after it and receives `"order-17"`. The router also runs after `receive_order`; it returns `"needs_approval"`, and **only** the method listening for that label runs. That is your if/else.

**Waiting for several steps.** `and_` waits for all, `or_` fires on the first:
```python
from crewai.flow.flow import and_

class CheckFlow(Flow):
    @start()
    def check_stock(self):
        print("stock checked")

    @start()
    def check_payment(self):
        print("payment checked")

    @listen(and_(check_stock, check_payment))
    def ship(self):
        print("both checks done: shipping")

CheckFlow().kickoff()
```
Prints `stock checked`, `payment checked`, then `both checks done: shipping`.

## Level 6 — A Flow that calls a Crew (Basics Part 7)
Each Flow step can be plain Python, one agent, or a whole Crew. The usual production pattern is **a Flow for the skeleton, Crews for the thinking**: a cheap check first, a router that stops early on a "no", and the full team only when it is worth it.

```python
class TripState(BaseModel):
    question: str = ""
    worth_it: str = ""
    plan: str = ""

class TripFlow(Flow[TripState]):

    @start()
    def quick_check(self):
        t = Task(
            description="Quick opinion for a student: {question}",
            expected_output="A verdict (yes, maybe or no) and 2 to 3 short reasons.",
            agent=guide,
            output_pydantic=TripVerdict,
        )
        out = Crew(agents=[guide], tasks=[t]).kickoff(inputs={"question": self.state.question})
        self.state.worth_it = out.pydantic.worth_it

    @router(quick_check)
    def decide(self):
        return "stop" if self.state.worth_it == "no" else "go"

    @listen("stop")
    def say_no(self):
        print("Quick check says no. Stopping here, the full team was never used.")

    @listen("go")
    def full_plan(self):
        r = Task(description="List 5 facts a student should know before this trip: {question}",
                 expected_output="A bulleted list of 5 facts.", agent=researcher)
        w = Task(description="Write a short plan from the facts.",
                 expected_output="One paragraph of at most 60 words.", agent=writer, context=[r])
        out = Crew(agents=[researcher, writer], tasks=[r, w]).kickoff(inputs={"question": self.state.question})
        self.state.plan = out.raw
        print(self.state.plan)

flow = TripFlow()
flow.state.question = "a weekend trip from Amman to Aqaba"
flow.kickoff()
```
The long lab's Step 9 does the same with the coffee-shop case.

## Reference: the fields and methods in detail
*Plain-language explanations of every box and method used above. Assumes no prior knowledge of CrewAI.*

### Anatomy of an Agent: role, goal and backstory

An LLM on its own is a general-purpose text machine. It has no job, no opinions and no point of view. The three required boxes of an Agent give it one. They are **not decoration**: CrewAI pastes them, almost word for word, into the **system prompt**, the hidden instruction that is sent to the model before your question (Module 2). Everything the model says afterwards is shaped by that text.

For our travel guide, this is **the real text CrewAI sends** (we printed it from the installed library):

```
You are Student Travel Guide. You have backpacked across 40 countries and you always think about cost first.
Your personal goal is: Give short, practical travel advice to students on a small budget
Current Task: <the task description goes here>

Provide your complete response:
```

Match it to the three boxes:

| Box | What it is | How it appears in the prompt | How it changes behaviour |
|---|---|---|---|
| **`role`** | The agent's **job title**: *who it is*. Short, 2 to 4 words. | `You are Student Travel Guide.` | Sets **vocabulary, expertise and viewpoint**. A "Cautious Accountant" and a "Marketing Enthusiast" answer the same question differently. |
| **`goal`** | **What it is trying to achieve**, and what it values. One sentence. | `Your personal goal is: ...` | Sets the **priority** when there is a trade-off. "Short, practical advice for students on a small budget" pushes it towards cheap, brief answers. |
| **`backstory`** | **Experience and character**: *how* it behaves and what it has seen. 1 to 3 sentences. | Placed straight after the role: `You have backpacked across 40 countries...` | Sets **style, habits and attitudes** ("always think about cost first", "never invent facts", "admits uncertainty"). |

(The word is **backstory**, as in the story behind a character in a film: where the character comes from and why it acts the way it does.)

**An important truth.** These three fields do not give the model new knowledge. A "travel guide" agent does not know more about Amman than the same model without the persona. What changes is **focus, tone and priorities**. The persona is a steering wheel, not an engine.

**Why it works.** A language model continues text in the most likely way. After "You are a careful accountant who has seen many businesses fail by launching too fast", the most likely continuation is cautious and numbers-first. After "You are an enthusiastic marketer", it is optimistic and creative. Same model, different continuation.

**Writing good ones**
- **Role**: a real job title, not a sentence. Good: `Market Researcher`. Weak: `Someone who helps with things`.
- **Goal**: one outcome the agent can be judged on. Good: `Find accurate facts and never invent numbers`. Weak: `Be helpful`.
- **Backstory**: behaviour and values, not biography trivia. Good: `You are sceptical and always say when the data is missing`. Weak: `You were born in 1985`.
- **Keep them consistent with each other and with the task.** A `role` of "Poet" with a task of "calculate VAT" will fight itself.
- Do not put the *task* in the backstory. Tasks go in `Task(description=...)`; the agent is a **reusable employee**, the task is **today's assignment**. One agent can do many tasks.

**Try it (no API key needed).** Create two agents with the same `role` but opposite `backstory` sentences and print them with `print(agent.backstory)`. Then, with a key, give both the same question using `.kickoff(...)` and compare.

#### The other Agent boxes you will meet
| Box | Meaning |
|---|---|
| `llm` | **Which model** powers this agent. Different agents may use different models. |
| `tools` | The list of **tools** it may call (Part 4). |
| `verbose=True` | **Print its thinking** step by step. Very useful while learning; switch off in production. |
| `max_iter` | A **safety limit** on how many think-act loops it may take, so it cannot loop forever. |
| `allow_delegation` | May it **ask other agents for help**? Needed for the manager in a hierarchical crew. |
| `max_rpm` | Maximum **requests per minute**, to stay within free-tier limits. |
| `memory`, `knowledge_sources` | Facts it can **remember** between runs, and **documents** it can search (long lab, Steps 5 and 6). |

### Anatomy of a Task: what goes inside the brackets?

Look again at the code we just wrote:

```python
explain = Task(
    description="Explain what an API is to a 12-year-old.",
    expected_output="Exactly 3 sentences, including one everyday analogy.",
    agent=guide,
)
```

`Task(...)` is a **form with named boxes**. Each line inside the brackets, such as `description="..."`, fills in one box. The box on the left of the `=` is the **field name** (CrewAI decides these names, you cannot invent new ones), and the value on the right is what you put in. So yes: a Task has a fixed structure, and everything you know about the job must fit into these boxes. Think of a work-order form in a company: "what to do", "what we expect", "who does it".

Only **two boxes are compulsory**: `description` and `expected_output`. Everything else is optional and has a sensible default. The table lists the ones you will actually use, most important first.

| Field | Required? | Plain meaning | Example |
|---|---|---|---|
| `description` | **Yes** | **What to do.** Written like an instruction to a colleague. May contain `{placeholders}` that are filled in at `kickoff(inputs=...)`. | `"List 5 facts about {topic}."` |
| `expected_output` | **Yes** | **What "done" looks like.** The agent reads this to know the format, length and level of detail. It is the strongest way to control the result. | `"A bulleted list of 5 facts."` |
| `agent` | Normally yes | **Who** does it. Must be an `Agent` you created earlier. (If you use a manager agent, the manager chooses and you can leave this out.) | `agent=researcher` |
| `context` | No | **Which earlier tasks' results this task needs.** A list of Task objects. | `context=[research]` |
| `tools` | No | Tools for **this task only**, instead of (more precisely: limiting) the agent's usual tools. | `tools=[add_vat]` |
| `output_pydantic` | No | Return the answer as a **typed Python object** with fixed fields instead of free text (Part 5). | `output_pydantic=TripVerdict` |
| `output_json` | No | Like the above, but the result is a plain dictionary. | `output_json=TripVerdict` |
| `output_file` | No | **Save the answer to a file** automatically. | `output_file="report.md"` |
| `guardrail` | No | A Python function that **checks the answer**; if the check fails, the agent must try again (long lab, Step 7). | `guardrail=my_check_function` |
| `human_input` | No | **Pause and ask a person** to approve the answer before continuing. | `human_input=True` |
| `async_execution` | No | Run this task **in the background** while the next one starts. Advanced. | `async_execution=True` |
| `name` | No | A short label that appears in logs. Nice for readability. | `name="research"` |
| `callback` | No | A function CrewAI calls **after** the task finishes (for example, to log or send a message). | `callback=my_function` |

**The three that matter first:** `description` (what), `expected_output` (what good looks like) and `agent` (who). Add `context` as soon as one task depends on another. Reach for the others only when you have a reason.

**Writing a good Task**
- `description` says *what to do*. `expected_output` says *how the answer should look*. Do not mix them: "Explain APIs" is the description; "3 sentences with an analogy" is the expected output.
- Be concrete. "A summary" is weak; "One paragraph of at most 50 words" is strong.
- If you can check the `expected_output` yourself in ten seconds (count sentences, count bullets), the agent can aim at it too.

### The same idea for Agent and Crew

Agent and Crew are also forms with fixed boxes. The important ones:

| Object | Compulsory boxes | Useful optional boxes |
|---|---|---|
| **Agent** | `role`, `goal`, `backstory` | `llm` (which model), `tools` (what it can call), `verbose` (print its thinking), `max_iter` (limit on thinking loops), `allow_delegation` (may it ask colleagues?), `max_rpm` (requests per minute), `memory`, `knowledge_sources` |
| **Crew** | `agents`, `tasks` | `process` (sequential or hierarchical), `verbose`, `memory`, `knowledge_sources`, `manager_llm` or `manager_agent` (for hierarchical), `max_rpm`, `planning` |

CrewAI will complain with a clear message if you leave a compulsory box empty or misspell a field name. That is a feature: the fixed structure catches mistakes early.

### Why the docstring matters: how an agent "reads" a tool

In ordinary Python, a **docstring** (the text in triple quotes right under the `def` line) is only a comment for humans. Python ignores it when running the function. **In CrewAI it is not a comment: it is the instruction manual the model reads.** Here is why.

**The model never sees your code.** An LLM only deals with text. It cannot open your function, read `price * (1 + vat_percent / 100)` and understand it. When an agent is created with `tools=[add_vat]`, CrewAI extracts **three things** from your function and puts them in the prompt:

| What CrewAI extracts | Where it comes from | What the model does with it |
|---|---|---|
| **Name** | `@tool("Add VAT")` | Uses it to refer to the tool when it decides to call it. |
| **Description** | The **whole docstring** | Decides **whether** this tool helps with the task, and **what to pass in**. |
| **Arguments and their types** | The **type hints**: `price: float, vat_percent: float` | Knows which values it must supply and their kind (number, text, ...). |

We printed what CrewAI really stores for our tool:

```
NAME: Add VAT
DESCRIPTION: Calculate the final price after adding VAT (sales tax).
    Inputs: the price before tax, and the VAT rate as a percentage (for example 16 for 16%).
    Returns the price including VAT, rounded to 2 decimals.
ARGUMENTS: price (number, required), vat_percent (number, required)
```

That block of text is **everything the model knows** about the tool. If it is vague, the model guesses.

**The flow, step by step**
1. You ask: "A laptop costs 849.50 before tax, VAT is 16%. What is the final price?"
2. The model reads its tool list. It sees *Add VAT: Calculate the final price after adding VAT...* and judges: "This matches, and I have both inputs."
3. It writes a **tool call**: `Add VAT(price=849.50, vat_percent=16)`. (Intent only; Module 4.)
4. **CrewAI runs your real Python function** and returns `985.42` as an Observation.
5. The model writes the final answer using that number.

Step 2 is decided **entirely by the docstring**. Step 3 is shaped by the docstring *and* the type hints.

**Three rules that follow**
1. **A docstring is compulsory.** If you write `@tool` on a function with no docstring, CrewAI stops with the error `Function must have a docstring`. It refuses to give the model a tool with no manual.
2. **Type hints are compulsory in practice.** Without `: float` or `: str` the model does not know what kind of value to send.
3. **Write the docstring for the model, not for yourself.** State (a) **what the tool does**, (b) **what each input means, with units and an example** ("VAT rate as a percentage, e.g. 16 for 16%"), (c) **what it returns**, and (d) **when to use it** or any limits ("the product must be one of: Espresso, Latte...").

**Why unit and example matter.** Our docstring says *"for example 16 for 16%"*. Without it the model might send `0.16` and the tool would add almost nothing. The function would still run without any error and quietly return a wrong number. Many "the agent is dumb" bugs are really "the docstring was ambiguous".

**Good versus weak**

| Weak (the agent guesses) | Strong (the agent knows) |
|---|---|
| `"""Does tax stuff."""` | `"""Calculate the final price after adding VAT (sales tax). Inputs: price before tax, and the VAT rate as a percentage (for example 16 for 16%). Returns the price including VAT, rounded to 2 decimals."""` |
| `"""Gets data."""` | `"""Summarise twelve months of sales for ONE product. The product must be one of: Espresso, Latte, Hot Tea. Returns total units and revenue."""` |

**Other good habits**: one tool = one job (narrow tools are used more reliably than one tool with ten options); a clear, specific name (`Add VAT`, not `Tool1`); return **short, readable text** (the model has to read the result); and if the input is invalid, return a **helpful message** (`"Unknown product. Use one of: ..."`) instead of crashing, so the agent can correct itself and try again.

**Python connection.** This is why in Python the docstring is also the text shown by `help(add_vat)`. CrewAI reuses a convention you already know and gives it a new audience: **the AI**.

### What does `kickoff` mean? (and the other "action" methods)

Until now, everything we wrote only **described** things. `Agent(...)`, `Task(...)` and `Crew(...)` build objects in memory; they are like writing a job advert, a work order and an org chart. **Nothing happens, no model is called, nothing costs money**, until you tell CrewAI to start. That start command is **`kickoff()`**.

The word comes from football: the *kick-off* is the moment the match begins. So:

> `something.kickoff(...)` means **"stop describing, begin the work now"**. The call waits until the work is finished and **returns the result**.

A **method** is just a function that belongs to an object, written `object.method(...)`. So `crew.kickoff()` means "ask this crew to start". The table below lists every such method you will meet, from the one you use constantly to the ones you can ignore for now.

| Method | Belongs to | What it does | Typical call |
|---|---|---|---|
| **`kickoff()`** | **Crew** | Run **all the tasks** of the crew in order, and return the final result. The values for `{placeholders}` go in `inputs`. | `crew.kickoff(inputs={"topic": "solar"})` |
| **`kickoff()`** | **Agent** | Run **one agent** on **one question** with no Task or Crew. The quickest way to try an agent. The question is passed as text. | `guide.kickoff("Two days in Amman?")` |
| **`kickoff()`** | **Flow** | Run the **whole flow**: begin at the `@start` step and follow the `@listen` and `@router` steps. | `OrderFlow().kickoff()` |
| `kickoff_for_each()` | Crew | Run the **same crew many times**, once per item of a list of inputs, and return a list of results. | `crew.kickoff_for_each([{"topic": "solar"}, {"topic": "wind"}])` |
| `kickoff_async()` / `akickoff()` | Crew, Agent | Start the work **without blocking** your program, so you can do something else meanwhile (in notebooks use `await`). Advanced. | `await crew.kickoff_async(inputs=...)` |
| `test()` | Crew | Run the crew several times and have a judge model **score the quality**. Used by developers when tuning a crew. | `crew.test(n_iterations=2, eval_llm="gemini/...")` |
| `train()` | Crew | Run the crew while a person **gives feedback**, which is saved so agents improve. Advanced. | `crew.train(n_iterations=2, filename="t.pkl")` |
| `replay()` | Crew | **Re-run from a chosen task** of an earlier run, without repeating the earlier ones. Advanced. | `crew.replay(task_id="...")` |
| `run()` | **Tool** | Run a tool **directly** with no AI, to test it. | `add_vat.run(price=80, vat_percent=16)` |
| `call()` | **LLM** | Send **one message straight to the model**, with no agent around it. | `llm.call("Say hello")` |

In this course you will use **`kickoff()`** (on Crew, Agent and Flow) all the time, `tool.run()` to test tools, and perhaps `kickoff_for_each()`. The rest are there so you recognise them in the documentation.

#### `inputs`: filling the placeholders
`inputs` is a dictionary (`{"name": value}`). Every `{name}` found inside a task `description`, an `expected_output`, or an agent's `role`, `goal` or `backstory` is replaced by the value before the work starts. That is why one crew can serve many topics:

```python
crew.kickoff(inputs={"topic": "solar power"})     # {topic} becomes "solar power"
```

#### What does `kickoff()` give back?
It returns a **result object**, not just text. Think of a parcel: the answer is inside, with a label on it. The most useful attributes (read them with a dot):

| Attribute | What it holds |
|---|---|
| `result.raw` | **The final answer as plain text.** This is what you print most of the time. |
| `result.pydantic` | The answer as a typed object, **if** the last task used `output_pydantic` (Part 5). |
| `result.json_dict` | The answer as a dictionary, **if** the last task used `output_json`. |
| `result.tasks_output` | A **list with one entry per task**, so you can see what each step produced. `result.tasks_output[0].raw` is the first task's text. |
| `result.token_usage` | **How much text the run consumed.** Tokens are what you pay for (Module 2). |

(`Agent.kickoff()` returns a similar object; `.raw` works there too.)

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
1. In the Level 5 example, if `amount` were `50` instead of `250`, which of `ask_manager` and `approve` would run, and would `log_order` still run?
2. What does `context=[research]` do, and what happens if you leave it out?
3. Why does a tool's docstring matter?
4. When would you choose a Flow over a Crew?

<details>
<summary>Answers</summary>

1. `approve` runs (the router returns `"auto_approve"`, so nothing runs for `"needs_approval"`), and `log_order` **still runs**: it listens to `receive_order`, not to the router, so the routing decision does not affect it.
2. It gives the writer the researcher's output as input. A sequential crew already passes earlier results along by default, so leaving it out often still works, but `context` makes the dependency explicit and lets you choose exactly which tasks feed which.
3. It is the only description the LLM has of what the tool does and how to call it. A vague docstring leads to the tool being ignored or misused.
4. When the order or the stopping rules must be predictable, cheap or auditable, and you can write them down in advance.
</details>

## Where to practice
1. Run Level 0, then change the persona and see how the answer shifts.
2. Build Level 2 with a topic you care about, then break it with a vague `expected_output`.
3. Add a custom tool, for example one that reads a local file (the lab's Exercise 2 does this).
4. Rebuild Level 5 with your own made-up steps and a router, then open the long lab at Step 9.
