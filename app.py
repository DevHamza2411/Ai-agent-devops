from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from Devops_tools import read_file, count_log_levels
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

# Initialize FastAPI App
app = FastAPI(title="DevOps Agent API", description="API for analyzing DevOps log files.")

# Define request body schema
class AgentQuery(BaseModel):
    question: str

# 1. Initialize LLM with local Ollama
llm = ChatOllama(
    model="llama3.2",
    base_url="http://localhost:11434",
    temperature=0
)

# 2. Define the DevOps log analyzer tool
@tool
def analyze_log_file(path: str) -> str:
    """
    This Tool reads a log file from a given path, counts log levels, and returns the log content.
    """
    try:
        # Print to terminal to see what path the LLM is actually passing
        print(f"\n🔍 DEBUG: Attempting to read file at path: '{path}'")
        
        raw_content = read_file(path)
        data = count_log_levels(raw_content)
        
        print(f"✅ DEBUG: Successfully read file! Counts: {data}")
        return f"Log analysis results for {path}: {str(data)}\n\nRaw Log Contents:\n{raw_content}"
    except Exception as e:
        error_msg = f"Error reading log file at {path}: {str(e)}"
        print(f"❌ DEBUG ERROR: {error_msg}")
        return error_msg

# Bind the tool to the LLM
tools_map = {"analyze_log_file": analyze_log_file}
llm_with_tools = llm.bind_tools([analyze_log_file])

# 3. Define System Prompt and Format Structure
SYSTEM_PROMPT = """You are a helpful DevOps assistant. Analyze the log file provided by the user using your tools.

Expected Output Format:
* **Summary:**
        + Total number of logs analyzed: <number>
        + Number of errors/ warnings/ info: <number> each
* **Top Error/Warning Messages:**
        + [list of top error/warning messages with frequency]
* **Top Error/Warning Causes:**
        + [list of top error/warning causes with frequency]
* **Critical Issues:**
        + [list of critical issues with details]"""

prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="messages"),
])

# 4. Agent Core Execution Logic
def run_devops_agent(user_question: str) -> str:
    messages = [HumanMessage(content=user_question)]
    
    prompt = prompt_template.invoke({"messages": messages})
    ai_message = llm_with_tools.invoke(prompt)
    messages.append(ai_message)
    
    if ai_message.tool_calls:
        for tool_call in ai_message.tool_calls:
            tool_to_run = tools_map[tool_call["name"]]
            tool_output = tool_to_run.invoke(tool_call["args"])
            messages.append(ToolMessage(content=tool_output, tool_call_id=tool_call["id"]))
        
        prompt = prompt_template.invoke({"messages": messages})
        final_response = llm_with_tools.invoke(prompt)
        return final_response.content
    else:
        return ai_message.content

# 5. Define the API Endpoint
@app.post("/v1/chat")
async def chat_endpoint(query: AgentQuery):
    try:
        answer = run_devops_agent(query.question)
        return {"status": "success", "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
