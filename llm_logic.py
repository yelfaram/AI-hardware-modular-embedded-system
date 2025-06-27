"""
AI Agent Workflow - ESP32 Application Idea Generator

This script implements the first two subtasks of a LangChain-based agent workflow:
1. Input Collection
2. Input Validation (with memory for back-and-forth dialog)

Each subtask is modular and designed for independent testing. Prompts are kept separate from code for clarity. 
We're using LangChain's Runnable interface (v0.3 style) along with `RunnableWithMessageHistory` to enable 
conversation memory across turns.

"""

"""
TO DO:
- Update to using v0.3 syntax of building chatbot (DONE)
    - init_chat_model                             (DONE)
    - langgraph for persistent memory             (DONE)
    - Source: v0.3 Documentation
"""

from dotenv import load_dotenv

from langchain.chat_models import init_chat_model                       # intance of llm chat model

from langchain.prompts import ChatPromptTemplate                        # Supports multi-message prompt formatting
from langchain.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser              # Extracts structured output from LLM
from langchain_core.exceptions import OutputParserException             # Catch invalid model output

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph

from typing import Sequence
from typing_extensions import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from pydantic import BaseModel, Field

from langchain.chains.sequential import SequentialChain                 # chain where the output of one chain is fed as input to the other

from prompts import (
    system_prompt, 
    first_task_prompt, 
    second_task_prompt
)

load_dotenv()

# ------------------------------------------
# Configuration
# ------------------------------------------
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")                                # Replace with Groq key
GROQ_MODELS  = {
    "fast": "llama3-8b-8192",
    "balanced": "deepseek-r1-distill-llama-70b",
    "powerful": "llama-3.3-70b-versatile"
}
GROQ_MODEL   = GROQ_MODELS["fast"]      

# Initialize Groq LLM
model = init_chat_model(GROQ_MODEL, model_provider="groq", temperature=0.3)

# ------------------------------------------
# State Definition
#   - track application parameters
#   - shared data structure (passed along edges between nodes)
#       - output of one node to the next can be taken as input

# Schema Definition
#   - structure of the state
#   - can be TypedDict or Pydantic
# ------------------------------------------
class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages] # add_messages(format='langchain-openai')
    message_review_flag: bool

workflow = StateGraph(state_schema=State)       # Define a new graph

# ------------------------------------------
# Node 1: Input Collection
#   - collects initial input from user: hardware components and preferred protocol
# ------------------------------------------

def collect_input(state: State):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("system", first_task_prompt),
        MessagesPlaceholder(variable_name="messages")
    ]).invoke(state)    # need invoke(state) to return formatted messages

    response = model.invoke(prompt)
    print("State of 1", state)
    return {"messages": [response], **state}

# ------------------------------------------
# Node 2: Input Validation
#   - checks if the components are compatible with the given protocol.
#   - adds memory support to handle user corrections or manual review.
# ------------------------------------------

def validate_input(state: State):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("system", second_task_prompt),
        MessagesPlaceholder(variable_name="messages")
    ]).invoke(state)

    response = model.invoke(prompt)
    return {"messages": [response]}

# ------------------------------------------
# Connect Graph Nodes
#
# Node Definition
#   - perform the actual work (execute logic; e.g. llm calls)
#
# Edge Definition
#   - define what happens next (flow of state)
# ------------------------------------------
# define nodes and edges
workflow.add_edge(START, "collect_input")
workflow.add_edge("collect_input", "validate_input")
workflow.add_node("collect_input", collect_input)
workflow.add_node("validate_input", validate_input)

# Add memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# ------------------------------------------
# Example Run
# ------------------------------------------
config             = {"configurable": {"thread_id": "abc123"}}
first_query        = "#### bme280, mpu6050, lcd1602 i2c ####"
second_query       = "Validate these components please."
manual_review_flag = False

# First input: component collection
input_messages = [HumanMessage(first_query)]
output = app.invoke(
    {"messages": input_messages, "manual_review_flag": manual_review_flag},
    config
)
print(output["messages"][-1].content)

# Second input: validation step
input_messages = [HumanMessage(second_query)]
output = app.invoke(
    {"messages": input_messages, "manual_review_flag": manual_review_flag},
    config
)
print(output["messages"][-1].content)