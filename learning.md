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