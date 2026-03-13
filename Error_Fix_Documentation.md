# Error Fix Documentation for resumebot.ipynb

This document outlines the errors identified in the `resumebot.ipynb` notebook, along with their causes, impacts, and step-by-step fixes. Each error includes code snippets showing the problematic code and the corrected version.

## 1. Incorrect Model Name in ChatGroq Initialization

### Error Description
The `ChatGroq` model is initialized with `"openai/gpt-oss-20b"`, which is not a valid Groq model. Groq's API supports models like `"llama3-8b-8192"`, `"mixtral-8x7b-32768"`, etc. Using an invalid model name will cause the API call to fail with an error such as "model not found" or similar.

### Impact
- The `parse_resume_node` function will raise an exception when invoking the LLM, halting the graph execution.
- No resume parsing will occur, leading to incomplete workflow.

### Fix
Change the model name to a valid Groq model. For example, use `"llama3-8b-8192"` for a fast and capable model.

#### Original Code (Error):
```python
llm = ChatGroq(model="openai/gpt-oss-20b")
```

#### Fixed Code:
```python
llm = ChatGroq(model="llama3-8b-8192")
```

#### Explanation
- Replace `"openai/gpt-oss-20b"` with a supported Groq model.
- Ensure your Groq API key has access to the chosen model.
- Test the model availability by checking Groq's documentation or running a simple invoke.

## 2. Potential JSON Parsing Failure in parse_resume_node

### Error Description
The code attempts to parse the LLM response as JSON by stripping markdown code blocks and using `json.loads()`. However, if the LLM does not return valid JSON (e.g., it includes extra text, malformed JSON, or refuses to format as JSON), this will raise a `JSONDecodeError`.

### Impact
- The function will crash with a JSON parsing error.
- The workflow stops, and no data is extracted or stored.

### Fix
Use LangChain's structured output binding to enforce JSON format, or add error handling for parsing.

#### Original Code (Error):
```python
response = llm.invoke([
    SystemMessage(content=system_prompt)
])

content = response.content.strip()
content = content.replace("```json", "").replace("```", "")
data = json.loads(content)
```

#### Fixed Code (Recommended):
```python
json_llm = llm.bind(
    response_format={"type": "json_object"}
)

response = json_llm.invoke([
    SystemMessage(content=system_prompt)
])

data = json.loads(response.content)
```

#### Alternative Fix with Error Handling:
```python
response = llm.invoke([
    SystemMessage(content=system_prompt)
])

content = response.content.strip()
content = content.replace("```json", "").replace("```", "")
try:
    data = json.loads(content)
except json.JSONDecodeError as e:
    print(f"JSON parsing error: {e}")
    # Fallback: manually extract or retry
    data = {}  # Or implement retry logic
```

#### Explanation
- The recommended fix uses `bind(response_format={"type": "json_object"})` to instruct the LLM to return JSON, reducing parsing errors.
- The alternative adds try-except to handle failures gracefully, preventing crashes.
- Always validate the JSON structure against expected keys.

## 3. Database Connection Failure in store_postgres_node

### Error Description
The code connects to PostgreSQL using `psycopg2.connect(DB_URI)`. If the `DB_URI` is incorrect (e.g., wrong host, port, database name, username, or password), or if PostgreSQL is not running, this will raise a connection error like `OperationalError`.

### Impact
- The `store_postgres_node` will fail, preventing data storage.
- The graph execution stops at this node.

### Fix
Verify and correct the `DB_URI`. Ensure PostgreSQL is installed, running, and the database exists. Use environment variables for credentials.

#### Original Code (Error):
```python
DB_URI = "postgresql://agentic:Anurag2004@localhost:5432/blog"

conn = psycopg2.connect(DB_URI)
```

#### Fixed Code:
```python
import os
DB_URI = os.getenv("DATABASE_URL", "postgresql://agentic:Anurag2004@localhost:5432/blog")

try:
    conn = psycopg2.connect(DB_URI)
except psycopg2.OperationalError as e:
    print(f"Database connection error: {e}")
    raise  # Or handle appropriately
```

#### Explanation
- Use `os.getenv` to load the URI from environment variables for security.
- Wrap the connection in a try-except to catch and log errors.
- Ensure PostgreSQL is running: `brew services start postgresql` (on macOS).
- Create the database if needed: `createdb blog`.

## 4. File Not Found Error in extract_text_node

### Error Description
The code opens a PDF file using `fitz.open(state["pdf_path"])`. If the file path is incorrect or the file does not exist, this will raise a `FileNotFoundError` or `RuntimeError` from PyMuPDF.

### Impact
- The `extract_text_node` fails, stopping the workflow.
- No text is extracted from the resume.

### Fix
Add file existence check and error handling. Use absolute paths or ensure relative paths are correct.

#### Original Code (Error):
```python
def extract_text_node(state: ResumeState):
    doc = fitz.open(state["pdf_path"])
    # ...
```

#### Fixed Code:
```python
import os

def extract_text_node(state: ResumeState):
    if not os.path.exists(state["pdf_path"]):
        raise FileNotFoundError(f"PDF file not found: {state['pdf_path']}")
    
    try:
        doc = fitz.open(state["pdf_path"])
    except Exception as e:
        raise RuntimeError(f"Error opening PDF: {e}")
    
    # ...
```

#### Explanation
- Check if the file exists using `os.path.exists()`.
- Wrap `fitz.open()` in a try-except for additional error handling.
- Ensure the path is correct; use absolute paths if needed.

## 5. Missing Dependencies

### Error Description
The code imports packages like `fitz`, `langchain_groq`, `psycopg2`, etc. If these are not installed, `ImportError` will be raised on import.

### Impact
- The notebook cells will fail to execute.
- Entire workflow unusable.

### Fix
Install the required packages using pip. Check `requirements.txt` and update it.

#### Original requirements.txt (Assuming minimal):
```
langchain
langchain-groq
pymupdf
psycopg2-binary
python-dotenv
```

#### Fixed requirements.txt:
Ensure all are listed:
```
langchain
langchain-groq
pymupdf
psycopg2-binary
python-dotenv
langgraph
```

#### Installation Command:
```bash
pip install -r requirements.txt
```

#### Explanation
- Run `pip install -r requirements.txt` to install all dependencies.
- Use `psycopg2-binary` for easier installation on macOS.
- Verify installations by importing in a Python shell.

## General Recommendations
- **Testing**: After fixes, run the graph with a sample PDF and verify each node.
- **Logging**: Add logging to track execution and errors.
- **Environment Variables**: Store sensitive data like API keys and DB URIs in `.env` files.
- **Validation**: Add checks for data integrity (e.g., ensure extracted fields are not empty).
- **Error Handling**: Implement retries or fallbacks for transient errors.

This documentation covers the main errors identified. Re-run the notebook after applying fixes and monitor for new issues.