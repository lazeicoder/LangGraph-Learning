# LangGraph Concepts Documentation

This documentation covers the key concepts from the LangGraph notebooks in the workspace, explained simply with code snippets where helpful.

## 1. Basic Workflow/Graph Building (from basics.ipynb)

### State
The State defines the data structure for your graph. Use TypedDict for type hints.

```python
from typing_extensions import TypedDict

class State(TypedDict):
    graph_info: str
```

**Use Cases:** Managing simple data flows like user preferences, game choices, or sequential tasks.  
**Flow:** Data starts at START, passes through nodes updating state, ends at END.  
**Alternative/Efficient Approaches:** For simple cases, use plain dicts without TypedDict. For validation, switch to Pydantic BaseModel for runtime checks.

### Nodes
Nodes are Python functions that take the State and return updated values.

```python
def start_play(state: State):
    return {"graph_info": state['graph_info'] + "I'm planning to play"}

def cricket(state: State):
    return {"graph_info": state['graph_info'] + " cricket!"}
```

**Use Cases:** Processing steps like data transformation, API calls, or decision logic.  
**Flow:** Each node receives state, modifies it, and passes to next node via edges.  
**Alternative/Efficient Approaches:** Use async functions for I/O-bound tasks. For complex logic, define node classes with methods.

### Conditional Edges
Use functions to decide the next node based on state.

```python
def random_play(state: State) -> Literal['cricket', 'football']:
    if random.random() > 0.5:
        return 'cricket'
    else:
        return 'football'
```

**Use Cases:** Branching logic like user choices, random selections, or conditional processing.  
**Flow:** After a node, the function evaluates state to choose the next path.  
**Alternative/Efficient Approaches:** For static conditions, use direct edges. For performance, cache decisions if state doesn't change often.

### Graph Construction
Build the graph with StateGraph, add nodes and edges, compile.

```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(State)
graph.add_node("start_play", start_play)
graph.add_node("cricket", cricket)
graph.add_edge(START, "start_play")
graph.add_conditional_edges("start_play", random_play)
graph.add_edge("cricket", END)

graph_builder = graph.compile()
```

**Use Cases:** Defining workflows for apps, games, or automation.  
**Flow:** START → nodes → conditional branches → END.  
**Alternative/Efficient Approaches:** For linear workflows, use LangChain's RunnableSequence instead of graphs for simplicity and better performance.

### Invocation
Run the graph with initial state.

```python
graph_builder.invoke({"graph_info": "Today is a pleasant day and "})
```

**Use Cases:** Executing the workflow with input data.  
**Flow:** Input state flows through the graph, updated at each node.  
**Alternative/Efficient Approaches:** Use streaming for large outputs. For batch processing, invoke multiple times in parallel.

## 2. Chains with Tools (from chains.ipynb)

### Messages as State
Use chat messages with reducers for conversation history.

```python
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
```

**Use Cases:** Chatbots, conversational AI, maintaining dialogue context.  
**Flow:** Messages accumulate via reducer, preserving history.  
**Alternative/Efficient Approaches:** Use LangChain's ConversationBufferMemory for simpler memory management without graphs.

### Binding Tools to LLM
Attach tools to the language model.

```python
llm_with_tools = llm.bind_tools([add])
```

**Use Cases:** Enabling LLMs to perform actions like calculations or searches.  
**Flow:** LLM decides to call tools based on input, tools execute, results fed back.  
**Alternative/Efficient Approaches:** For static tools, pre-bind. Use toolkits from LangChain for common integrations.

### ToolNode and Conditions
Use prebuilt nodes for tool execution.

```python
from langgraph.prebuilt import ToolNode, tools_condition

builder.add_node("tools", ToolNode(tools=[add]))
builder.add_conditional_edges("llmtool", tools_condition)
```

**Use Cases:** Automating tool calls in workflows.  
**Flow:** If LLM requests tool, route to ToolNode; else, continue.  
**Alternative/Efficient Approaches:** Custom tool nodes for error handling. Use LangChain agents for built-in tool routing.

## 3. Simple Chatbot (from chatbot.ipynb)

### Basic Chatbot State
State with messages for conversation.

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]
```

**Use Cases:** Basic Q&A bots, simple assistants.  
**Flow:** User input → LLM → response, messages build history.  
**Alternative/Efficient Approaches:** Use LangChain's ConversationChain for out-of-the-box chat without custom graphs.

### LLM Node
Node that calls the LLM with current messages.

```python
def superbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}
```

**Use Cases:** Generating responses in chat applications.  
**Flow:** Node invokes LLM, appends response to messages.  
**Alternative/Efficient Approaches:** Use RunnableLambda for simpler function wrapping.

### Graph and Invocation
Simple linear graph.

```python
graph = StateGraph(State)
graph.add_node("SuperBot", superbot)
graph.add_edge(START, "SuperBot")
graph.add_edge("SuperBot", END)
graph_builder = graph.compile()

graph_builder.invoke({"messages": "Hello i'm Anurag"})
```

**Use Cases:** Straightforward chat interfaces.  
**Flow:** Input → LLM node → output.  
**Alternative/Efficient Approaches:** For single-step, use direct LLM calls. Add memory buffers for persistence.

### Streaming
Stream responses in real-time.

```python
for event in graph_builder.stream({"messages": "Hello"}, stream_mode="values"):
    print(event)
```

**Use Cases:** Real-time chat, progressive output.  
**Flow:** Events stream as graph processes, showing intermediate states.  
**Alternative/Efficient Approaches:** Use async streaming for better concurrency.

## 4. Chatbot with Multiple Tools (from chatbotwithtools.ipynb)

### Integrating External Tools
Use tools like Arxiv, Wikipedia, DuckDuckGo search.

```python
from langchain_community.tools import WikipediaQueryRun, ArxivQueryRun

arxiv = ArxivQueryRun(api_wrapper=ArxivAPIWrapper(top_k_results=3))
wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
search = DuckDuckGoSearchResults()
```

**Use Cases:** Research assistants, knowledge retrieval.  
**Flow:** LLM queries tools, gets data, incorporates into response.  
**Alternative/Efficient Approaches:** Use LangChain toolkits for bundled tools. Cache results for repeated queries.

### Custom Tools
Define your own functions as tools.

```python
def add(a: int, b: int) -> int:
    return a + b

tools = [arxiv, wiki, search, add]
```

**Use Cases:** Domain-specific actions like math, APIs.  
**Flow:** Tools called by LLM, results used in conversation.  
**Alternative/Efficient Approaches:** Use structured tools with Pydantic schemas for better validation.

### Agent Creation
Create agents with memory.

```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(llm, tools=tools, checkpointer=InMemorySaver())
```

**Use Cases:** Persistent conversations, multi-step tasks.  
**Flow:** Agent manages state, tools, and memory across interactions.  
**Alternative/Efficient Approaches:** Use LangChain's AgentExecutor for simpler agent setup without custom graphs.

### Persistent Memory with Postgres
Use database for long-term memory.

```python
from langgraph.checkpoint.postgres import PostgresSaver

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    agent = create_agent(llm, tools=tools, checkpointer=checkpointer)
```

**Use Cases:** Apps needing durable state across restarts.  
**Flow:** Checkpoints saved to DB, loaded on resume.  
**Memory Storage:** PostgresSaver stores data in Postgres tables (e.g., `checkpoints`). State, messages, and thread IDs are serialized as JSON or binary blobs in columns like `checkpoint` (JSONB for metadata) and `metadata`. This allows persistence, versioning, and querying of conversation history.  
**Alternative/Efficient Approaches:** InMemorySaver for fast, volatile memory; Redis for distributed caching.

### Resume Parsing
Integrate with Apify for document processing.

```python
from apify_client import ApifyClient

client = ApifyClient(apify_key)
run = client.actor("vivid_astronaut/resume-parser").call(run_input=run_input)
```

**Use Cases:** HR tools, document analysis.  
**Flow:** Upload resume → Apify processes → extract skills/experience.  
**Alternative/Efficient Approaches:** Use local OCR/PDF parsers for offline processing.

## 5. State Schema Options (from dataclass.ipynb)

### TypedDict
Basic state with TypedDict.

```python
class TypeDictState(TypedDict):
    name: str
    game: Literal["chess", "football", "cricket"]
```

**Use Cases:** Simple, type-safe state definitions.  
**Flow:** State passed between nodes with type checking.  
**Alternative/Efficient Approaches:** Plain dicts for no typing; DataClasses for more features.

### DataClasses
Use Python's dataclasses for state.

```python
from dataclasses import dataclass

@dataclass
class DataClassState:
    name: str
    game: Literal["chess", "cricket", "badminton"]
```

**Use Cases:** More structured data with auto-generated methods.  
**Flow:** Similar to TypedDict, but with class benefits.  
**Alternative/Efficient Approaches:** Pydantic for validation; NamedTuples for immutable data.

### Pydantic
For validation and more complex schemas.

```python
from pydantic import BaseModel

class PyState(BaseModel):
    name: str
    age: int
```

**Use Cases:** Validated, complex state with auto-validation.  
**Flow:** Ensures data integrity in graphs.  
**Alternative/Efficient Approaches:** Use for APIs; TypedDict for lighter weight.

These concepts form the foundation of building workflows, chatbots, and agents with LangGraph, integrating LLMs, tools, and persistent state.

---

## 6. End‑to‑End Walkthrough of Each Notebook and Problem

This section gives a **story-style, step‑by‑step explanation** of every notebook in this repo:

- **`basics.ipynb`** – building your first LangGraph workflow with branching.
- **`chains.ipynb`** – creating a tool‑using chain (LLM + tools).
- **`chatbot.ipynb`** – turning LangGraph into a simple chatbot engine.
- **`chatbotwithtools.ipynb`** – building a smarter agent with external tools and memory.
- **`dataclass.ipynb`** – understanding different ways to model Graph State.
- **`resumebot.ipynb`** – building a resume parser and storing structured data in Postgres.

Each subsection below answers:

- **What problem are we solving?**
- **Which LangGraph concepts are used?**
- **How does the code solve it (step‑by‑step)?**
- **Where should you pay attention / extend it?**

---

## 6.1 `basics.ipynb` – Simple Workflow / Game Selector

### Problem We’re Solving

“I want to **define a small workflow** (graph) where:

- I start with some text (`graph_info`),
- add a sentence about planning to play,
- then **randomly choose** between *cricket* and *football*,
- and end the workflow with a final message.”

This notebook teaches you how to go from **zero to a compiled LangGraph** with:

- **State** (what data flows through),
- **Nodes** (steps that modify the state),
- **Conditional edges** (where to go next),
- **Graph construction & invocation**.

### Concepts and Approach

- **State as a TypedDict** – to define the keys and types that travel through the graph:

```python
from typing_extensions import TypedDict

class State(TypedDict):
    graph_info: str
```

- **Node functions** – simple Python functions taking `state` and returning a **partial state update**:

```python
def start_play(state: State):
    print("Start_play has been called")
    return {"graph_info": state['graph_info'] + "I'm planning to play"}

def cricket(state: State):
    print("Cricket node has been called!")
    return {"graph_info": state['graph_info'] + " cricket!"}

def football(state: State):
    print("Football node has been called!")
    return {"graph_info": state['graph_info'] + " football!!"}
```

- **Conditional routing** – returning a string that indicates which node to go to:

```python
import random 
from typing import Literal

def random_play(state: State) -> Literal['cricket', 'football']:
    if random.random() > 0.5:
        return 'cricket' 
    else: 
        return 'football'
```

- **Graph construction** – wiring everything together:

```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(State)

graph.add_node("start_play", start_play)
graph.add_node("cricket", cricket)
graph.add_node("football", football)

graph.add_edge(START, "start_play")
graph.add_conditional_edges("start_play", random_play)
graph.add_edge("cricket", END)
graph.add_edge("football", END)

graph_builder = graph.compile()
```

- **Invocation** – executing the workflow:

```python
graph_builder.invoke({
    "graph_info": "Today is a pleasant day and "
})
```

**Intuition:**  
State is like a **dictionary passed from step to step**, each node **adds or modifies** keys, and LangGraph handles **routing and execution order**.

---

## 6.2 `chains.ipynb` – Tool‑Using LLM Chain

### Problem We’re Solving

“I want to build a **chat‑like chain** where:

- the user asks a question (e.g. ‘What is 43 + 6859?’),
- the **LLM decides** that it should call a tool (`add`),
- the graph actually **executes that tool**,
- the final answer includes the **tool result**.”

This notebook shows how to:

- Represent **messages** as graph state,
- **Bind tools** to an LLM,
- Use **prebuilt `ToolNode`** + `tools_condition` for automatic tool routing.

### Concepts and Approach

- **Defining a tool**:

```python
def add(a: int, b: int) -> int:
    """
    Adds two integers together.
    """
    return a + b
```

- **Creating an LLM that is aware of tools**:

```python
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

llm = ChatGroq(model="llama-3.1-8b-instant")
llm_with_tools = llm.bind_tools([add])

tool_calls = llm_with_tools.invoke([
    HumanMessage(content="What is 457867349478 + 8924398743895?")
])
```

- **State with message history and a reducer**:

```python
from typing_extensions import TypedDict
from typing import Annotated
from langchain_core.messages import AnyMessage, AIMessage, HumanMessage
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
```

Here, **`add_messages`** is a reducer that **appends** new messages to the list, giving you automatic conversation history.

- **LLM node that uses tools**:

```python
def llm_tool(state: State):
    return {
        "messages": [
            llm_with_tools.invoke(state["messages"])
        ]
    }
```

- **First simple graph (no actual tool execution yet)**:

```python
from langgraph.graph import StateGraph, START, END
from IPython.display import display, Image

builder = StateGraph(State)
builder.add_node("llmtool", llm_tool)
builder.add_edge(START, "llmtool")
builder.add_edge("llmtool", END)

graph = builder.compile()
display(Image(graph.get_graph().draw_mermaid_png()))
```

Invocation:

```python
messages = graph.invoke({"messages": "What is 43 + 6859?"})
for message in messages["messages"]:
    message.pretty_print()
```

You see that the **LLM wants to call `add`**, but we still need something to **execute** the tool call.

- **Adding `ToolNode` + conditional edges** – this is the key LangGraph pattern:

```python
from langgraph.prebuilt import ToolNode, tools_condition

builder = StateGraph(State)

builder.add_node("tools", ToolNode(tools=[add]))
builder.add_node("llmtool", llm_tool)

builder.add_edge(START, "llmtool")
builder.add_conditional_edges("llmtool", tools_condition)
builder.add_edge("tools", END)

graph = builder.compile()
```

Now:

```python
messages = graph.invoke({"messages": "What is 43 + 6859?"})
for message in messages["messages"]:
    message.pretty_print()
```

You will see:

- Human message,
- AI message with a **tool call**,
- Tool message with the **numeric result**.

**Intuition:**  
The LLM decides *what* to do (call tool or answer directly), while LangGraph decides *how* to move between nodes (`llmtool → tools → END`) using `tools_condition`.

---

## 6.3 `chatbot.ipynb` – Simple LangGraph Chatbot

### Problem We’re Solving

“I want a **minimal chatbot** built on LangGraph:

- User sends a message,
- LLM responds,
- The flow is simple (one LLM node),
- I can also **stream** responses.”

This notebook focuses on:

- Defining chat **state**,
- Creating a **single LLM node**,
- Building a **linear graph**,
- Using **streaming** to get partial outputs.

### Concepts and Approach

- **State with a messages list and reducer**:

```python
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
```

- **LLM setup (Groq + environment)**:

```python
import os 
from dotenv import load_dotenv

load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

from langchain_groq import ChatGroq
llm = ChatGroq(model="llama-3.1-8b-instant")
```

- **Node that calls the LLM**:

```python
def superbot(state: State):
    return {
        "messages": [
            llm.invoke(state["messages"])
        ]
    }
```

- **Graph construction**:

```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(State)
graph.add_node("SuperBot", superbot)
graph.add_edge(START, "SuperBot")
graph.add_edge("SuperBot", END)

graph_builder = graph.compile()
```

- **Basic invocation**:

```python
graph_builder.invoke({
    "messages": "Hello i'm Anurag, and i'm a Software Engineer."
})
```

This returns both the **human message** and the **AI message** as a list.

- **Streaming responses**:

```python
for event in graph_builder.stream(
    {"messages": "Hello i'm Anurag"},
    stream_mode="values",
):
    print(event)
```

This prints intermediate states as the message list gets updated.

**Key Learning:**  
Even a **very simple chatbot** benefits from LangGraph’s structure – you can later add more nodes (tools, memory, routing) without redesigning everything.

---

## 6.4 `chatbotwithtools.ipynb` – Multi‑Tool Agent with Memory and Resume Parsing

### Problem We’re Solving

“I want a **powerful agentic assistant** that can:

- Search the web (DuckDuckGo),
- Query external knowledge (Arxiv, Wikipedia),
- Use **custom tools** (like `add`),
- Persist state in **Postgres** using checkpointers,
- Even integrate external services (like Apify) for tasks such as **resume parsing**.”

This notebook covers:

- **Multiple tools** (research tools + custom code),
- **Agent creation** with memory/checkpointing,
- **Postgres‑backed memory**,
- High‑level flows like **resume analysis** and **cover‑letter generation**.

### Concepts and Approach

- **External tools** (examples):

```python
from langchain_community.tools import WikipediaQueryRun, ArxivQueryRun
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper

arxiv = ArxivQueryRun(api_wrapper=ArxivAPIWrapper(top_k_results=3))
wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
search = DuckDuckGoSearchResults()
```

- **Custom tool (e.g. `add`)**:

```python
def add(a: int, b: int) -> int:
    return a + b

tools = [arxiv, wiki, search, add]
```

- **Agent + checkpointer (in‑memory)**:

```python
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent

llm = ChatGroq(model="llama-3.1-8b-instant")
checkpointer = InMemorySaver()

agent = create_agent(llm, tools=tools, checkpointer=checkpointer)
```

Now the agent can:

- Receive user messages,
- Decide **which tools** to call,
- Store intermediate state in memory.

- **Moving to Postgres for persistent memory**:

```python
from langgraph.checkpoint.postgres import PostgresSaver

DB_URI = "postgresql://user:password@localhost:5432/db_name"

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    agent = create_agent(llm, tools=tools, checkpointer=checkpointer)
```

This ensures that **conversation state and checkpoints** survive process restarts and can be retrieved later using thread IDs.

- **Example advanced workflow – HR / cover‑letter agent**

The notebook also defines a **system prompt** that makes the LLM behave like a senior HR professional, then:

- Accepts a **job description**,
- Uses tools/memory if needed,
- Produces a **tailored cover letter** that is keyword‑rich and role‑aligned.

**Intuition:**  
Here, LangGraph is used less for explicit node‑by‑node wiring and more as a **foundation for agent + memory orchestration**. Tools, LLM, and database‑backed state are combined into a single, reusable agent.

---

## 6.5 `dataclass.ipynb` – State Schema Strategies (TypedDict vs Dataclass vs Pydantic)

### Problem We’re Solving

“In my graphs, how should I **define my State**?

- Is a simple `dict` enough?
- When should I use `TypedDict`, `dataclass`, or `Pydantic`?
- What do I gain/lose with each option?”

This notebook is a **conceptual comparison** of state schema options.

### Concepts and Approach

- **TypedDict** – lightweight, static type hints:

```python
from typing_extensions import TypedDict
from typing import Literal

class TypeDictState(TypedDict):
    name: str
    game: Literal["chess", "football", "cricket"]
```

**When to use:**  
You want **type hints** and editor support, with almost no runtime overhead.

- **Dataclasses** – Pythonic, object‑oriented state:

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class DataClassState:
    name: str
    game: Literal["chess", "cricket", "badminton"]
```

**When to use:**  
You prefer **methods**, default values, and standard Python semantics, while keeping things fairly lightweight.

- **Pydantic models** – validated, strict, API‑friendly:

```python
from pydantic import BaseModel

class PyState(BaseModel):
    name: str
    age: int
```

**When to use:**  
You need:

- **Input validation**,
- Clear error messages,
- JSON serialization,
- Stronger guarantees about data shape (e.g. in APIs or production systems).

**Takeaway:**  
All three can be used as LangGraph state. Choose based on **type‑safety needs, runtime performance, and integration requirements**.

---

## 6.6 `resumebot.ipynb` – Resume Parsing and Storage Pipeline

### Problem We’re Solving

“Given a **PDF resume**, I want to:

- Extract the raw text,
- Ask an LLM to **parse** it into a structured JSON (name, email, skills, experience, etc.),
- **Store** that structured data in a Postgres database,
- All orchestrated through a **LangGraph workflow**.”

This notebook demonstrates a **real-world, end‑to‑end pipeline**:

- File I/O (**PyMuPDF / `fitz`**),
- LLM‑based parsing,
- Data cleaning/normalization,
- **Postgres** persistence,
- Graph wiring (`extract_text → parse_resume → store_db → END`).

### Concepts and Approach

- **State definition for resume data**:

```python
from typing import TypedDict, List

class ResumeState(TypedDict, total=False):
    pdf_path: str
    resume_text: str
    name: str
    email: str
    phone: str
    skills: List[str]
    education: List[str]
    experience: List[str]
    projects: List[str]
```

- **Node 1 – Extract text from PDF**:

```python
import fitz  # PyMuPDF

def extract_text_node(state: ResumeState):
    doc = fitz.open(state["pdf_path"])

    text = ""
    for page in doc:
        text += page.get_text()

    return {"resume_text": text}
```

- **Node 2 – Parse resume with LLM into structured JSON**:

```python
import json
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage

llm = ChatGroq(model="openai/gpt-oss-20b")

def parse_resume_node(state: ResumeState):
    system_prompt = f"""
        You're an expert Resume Parsing AI agent.
        Go through and understand the Resume.
        Extract structured information.

        Return ONLY valid JSON in this format:
        {{
            "name": "",
            "email": "",
            "phone": "",
            "skills": [],
            "education": [],
            "experience": [],
            "projects": []
        }}

        Resume:
            {state["resume_text"]}
    """

    response = llm.invoke([SystemMessage(content=system_prompt)])

    content = response.content.strip()
    content = content.replace("```json", "").replace("```", "")
    data = json.loads(content)

    return data
```

Here we:

- Prompt the LLM to output **strict JSON**,
- Clean out Markdown fences (```json ... ```),
- Parse the JSON string into Python with `json.loads`,
- Return the structured data, which merges into `ResumeState`.

- **Node 3 – Store structured data into Postgres**:

```python
import psycopg2
import json

DB_URI = "postgresql://agentic:Anurag2004@localhost:5432/blog"

def normalize_list(value):
    if not value:
        return []
    cleaned = []
    for item in value:
        if isinstance(item, dict):
            cleaned.append(json.dumps(item))
        else:
            cleaned.append(str(item))
    return cleaned

def store_postgres_node(state: ResumeState):
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id SERIAL PRIMARY KEY,
        name TEXT,
        email TEXT,
        phone TEXT,
        skills TEXT[],
        education TEXT[],
        experience TEXT[],
        projects TEXT[]
    )
    """)

    cur.execute("""
    INSERT INTO resumes
    (name, email, phone, skills, education, experience, projects)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        state.get("name"),
        state.get("email"),
        state.get("phone"),
        normalize_list(state.get("skills")),
        normalize_list(state.get("education")),
        normalize_list(state.get("experience")),
        normalize_list(state.get("projects")),
    ))

    conn.commit()
    conn.close()

    return state
```

Key points:

- **`CREATE TABLE IF NOT EXISTS`** makes the notebook idempotent.
- `normalize_list` converts lists of dicts or other objects into a form acceptable for a `TEXT[]` column.

- **Graph wiring**:

```python
from langgraph.graph import StateGraph, START, END
from IPython.display import display, Image

workflow = StateGraph(ResumeState)

workflow.add_node("extract_text", extract_text_node)
workflow.add_node("parse_resume", parse_resume_node)
workflow.add_node("store_db", store_postgres_node)

workflow.add_edge(START, "extract_text")
workflow.add_edge("extract_text", "parse_resume")
workflow.add_edge("parse_resume", "store_db")
workflow.add_edge("store_db", END)

graph = workflow.compile()
display(Image(graph.get_graph().draw_mermaid_png()))
```

- **Invoking the pipeline**:

```python
result = graph.invoke({"pdf_path": "resumes/Anurag_Mukherjee_Resume.pdf"})
print(result)
```

The output contains the full `ResumeState` after parsing and storage.

**Intuition:**  
This notebook shows how LangGraph can coordinate **multiple different concerns** (files, LLMs, databases) into a clean, sequential pipeline that you can **inspect, visualize, and extend**.

---

## 7. How All These Pieces Fit Together

- **`basics.ipynb`** teaches you **graph primitives** (state, nodes, edges, conditional routing).
- **`chains.ipynb`** adds **LLMs and tools**, turning graphs into **intelligent chains**.
- **`chatbot.ipynb`** shows a **full chatbot loop** with streaming.
- **`chatbotwithtools.ipynb`** evolves this into an **agent** with **external tools and memory** (including Postgres).
- **`dataclass.ipynb`** helps you choose the **right schema strategy** for your graph state.
- **`resumebot.ipynb`** demonstrates a **production‑style workflow**: document ingestion → LLM parsing → database persistence.

Together, these notebooks illustrate **how to solve real problems with LangGraph**:

- From simple control‑flow graphs,
- To tool‑using chains,
- To stateful chatbots,
- To end‑to‑end, database‑backed AI workflows.

You can use this `README.md` as a **roadmap**: open each notebook in order and follow along with the explanations and snippets above to fully understand the concepts and problems being solved.